const roomName = JSON.parse(document.getElementById('room-name').textContent);
const uuid = JSON.parse(document.getElementById('uuid').textContent);
const localVideo = document.getElementById('local_video');
const remoteVideosContainer = document.getElementById('remote_videos_container');
let localStream = null;
let remoteVideos = [];
let isOffer = false;
let peerConnections = [];
let usernames = [];

const ws = new WebSocket(
    'ws://'
    + window.location.host
    + '/ws/video/'
    + roomName
    + '/'
);

ws.onopen = (evt) => {
    console.log('ws open()');
};
ws.onerror = (err) => {
    console.error('ws onerror() ERR:', err);
};
ws.onmessage = (evt) => {
    const message = JSON.parse(evt.data);
    if (message.from_uuid === uuid){
        return;
    }
    if (message.to_uuid === uuid || message.to_uuid === 'every'){
        console.log(`from: ${message.from_uuid} to: ${message.to_uuid}`)
        console.log('ws onmessage() data:', evt.data);
        switch(message.type){
            case 'offer': {
                console.log('Received offer ...');
                setOffer(message, message.from_uuid);
                break;
            }
            case 'answer': {
                console.log('Received answer ...');
                setAnswer(message, message.from_uuid);
                break;
            }
            case 'candidate': {
                console.log('Received ICE candidate ...');
                const candidate = new RTCIceCandidate(message.ice);
                console.log(candidate);
                addIceCandidate(candidate, message.from_uuid);
                break;
            }
            case 'close': {
                console.log('Received close ...');
                if (isConnectedWith(message.from_uuid)) {
                    disconnect(message.from_uuid);
                }
                break;
            }
            case 'callOffer': {
                console.log('Received callOffer ...');
                connect(message.from_uuid)
                break;
            }
            case 'message': {
                console.log('Received message ...');
            }
            default: { 
                console.log("Invalid message"); 
                break;              
                }         
        }
    } else {
        return;
    }
};

// ICE candaidate???????????????????????????
function addIceCandidate(candidate, from_uuid) {
    if (! isConnectedWith(from_uuid)) {
        console.warn('NOT CONNEDTED or ALREADY CLOSED with id=' + from_uuid + ', so ignore candidate');
        return;
    }
    let peerConnection = getConnection(from_uuid);
    if (peerConnection){
        peerConnection.addIceCandidate(candidate);
    } else {
        console.error('PeerConnection not exist!');
        return;
    }
}

// ICE candidate????????????????????????
function sendIceCandidate(candidate, to_uuid) {
    console.log('---sending ICE candidate ---');
    const message = JSON.stringify({ type: 'candidate', ice: candidate, from_uuid: uuid, to_uuid: to_uuid });
    console.log('sending candidate=' + message);
    ws.send(message);
}

// WebRTC??????????????????????????????
function prepareNewConnection(isOffer, from_uuid) {
    const pc_config = {"iceServers":[ {"urls":"stun:stun.1.google.com:19302"} ]};
    const peer = new RTCPeerConnection(pc_config);

    // ???????????????MediStreamTrack??????????????????
    peer.ontrack = evt => {
        console.log('-- peer.ontrack()');
        let remoteVideo = addRemoteVideoElement(from_uuid);
        playVideo(remoteVideo, evt.streams[0]);
    };

    // ICE Candidate????????????????????????????????????
    peer.onicecandidate = evt => {
        if (evt.candidate) {
            console.log(evt.candidate);
            sendIceCandidate(evt.candidate, from_uuid);
        } else {
            console.log('empty ice event');
        }
    };

    // Offer??????????????????????????????????????????????????????????????????
    peer.onnegotiationneeded = async () => {
        try {
            if(isOffer){
                let offer = await peer.createOffer();
                console.log('createOffer() succsess in promise');
                await peer.setLocalDescription(offer);
                console.log('setLocalDescription() succsess in promise');
                sendSdp(peer.localDescription, from_uuid);
            }
        } catch(err){
            console.error('setLocalDescription(offer) ERROR: ', err);
        }
    }

    // ICE??????????????????????????????????????????????????????
    peer.oniceconnectionstatechange = function() {
        console.log('ICE connection Status has changed to ' + peer.iceConnectionState);
        switch (peer.iceConnectionState) {
            case 'closed':
            case 'failed':
                if (isConnectedWith[from_uuid]) {
                    hangUp()
                }
                break;
            case 'disconnected':
                disconnect(from_uuid)
                break;
        }
    };

    // ???????????????MediaStream?????????????????????????????????
    if (localStream) {
        console.log('Adding local stream...');
        localStream.getTracks().forEach(track => peer.addTrack(track, localStream));
    } else {
        console.warn('no local stream, but continue.');
    }

    return peer;
}

// Send SDP
function sendSdp(sessionDescription, to_uuid) {
    console.log('---sending sdp ---');
    const message = JSON.stringify({ type: sessionDescription.type, sdp: sessionDescription.sdp, from_uuid: uuid, to_uuid: to_uuid });
    console.log('sending SDP=' + message);
    ws.send(message);
}

// Handle Call Offer
function connect(from_uuid) {
    if (isConnectedWith(from_uuid)) {
        console.warn('peer already exist.');
    } else {
        console.log('make Offer');
        peerConnection = prepareNewConnection(true, from_uuid);
        addConnection(from_uuid, peerConnection);
    }
}

// Send Call Offer
function callOffer(){
    const message = JSON.stringify({ type: 'callOffer', from_uuid: uuid, to_uuid: 'every' });
    console.log('sending callOffer=' + message);
    ws.send(message);
}


// Generate Answer SDP
async function makeAnswer(from_uuid) {
    console.log('sending Answer. Creating remote session description...' );
    let peerConnection = getConnection(from_uuid);
    if (! peerConnection) {
        console.error('peerConnection NOT exist!');
    }
    try{
        let answer = await peerConnection.createAnswer();
        console.log('createAnswer() succsess in promise');
        await peerConnection.setLocalDescription(answer);
        console.log('setLocalDescription() succsess in promise');
        sendSdp(peerConnection.localDescription, from_uuid);
    } catch(err){
        console.error(err);
    }
}


// Set Offer SDP
async function setOffer(sessionDescription, from_uuid) {
    if (isConnectedWith(from_uuid)){
        console.error('connected offer');
    }
    let peerConnection = prepareNewConnection(false, from_uuid);
    addConnection(from_uuid, peerConnection);
    try{
        await peerConnection.setRemoteDescription(sessionDescription);
        console.log('setRemoteDescription(answer) succsess in promise');
        makeAnswer(from_uuid);
    } catch(err){
        console.error('setRemoteDescription(offer) ERROR: ', err);
    }
}

// Set Answer SDP
async function setAnswer(sessionDescription, from_uuid) {
    let peerConnection = getConnection(from_uuid);
    if (! peerConnection) {
        console.error('peerConnection NOT exist!');
        return;
    }
    try{
        await peerConnection.setRemoteDescription(sessionDescription);
        console.log('setRemoteDescription(answer) succsess in promise');
    } catch(err){
        console.error('setRemoteDescription(answer) ERROR: ', err);
    }
}

// Hang up
function hangUp() {
    const message = JSON.stringify({ type: 'close', from_uuid: uuid, to_uuid: 'every' });
    console.log('sending close message');
    ws.send(message);
    localVideo.pause();
    let stream = localVideo.srcObject
    let tracks = stream.getTracks();
    tracks.forEach(function(track) {
        track.stop();
    });
    localStream = null;
    localVideo.srcObject = null;
    return;
}

// Disconnect P2P
function disconnect(from_uuid) {
    console.log('disconnecting')
    let peerConnection = getConnection(from_uuid);
    peerConnection.close();
    deleteConnection(from_uuid);
    let remoteVideo = getRemoteVideoElement(from_uuid);
    cleanupRemoteVideoElement(remoteVideo);
}


// ------------------ Media -----------------
// Add Remote Video Element
function addRemoteVideoElement(uuid) {
    let video = createVideoElement(`remote_video_${uuid}`);
    remoteVideos[uuid] = video;
    return video;
}

// Create Remote Video Element
function createVideoElement(elementId) {
    let video = document.createElement('video');
    video.id = elementId;
    video.width = '160';
    video.height = '120';
    video.autoplay = true;
    video.muted = true;
    video.playsInline = true;
    video.className = 'rounded'
    remoteVideosContainer.appendChild(video);
    return video;
}

// Start Local Video
async function startVideo() {
    try{
        localStream = await navigator.mediaDevices.getUserMedia({video: true, audio: false});
        playVideo(localVideo,localStream);
        const local_username_display = document.getElementById('local_username_display');
        local_username_display.innerText = `You`;
    } catch(err){
        console.error('mediaDevice.getUserMedia() error:', err);
    }
}

// Play Video
async function playVideo(element, stream) {
    element.srcObject = stream;
    try {
        await element.play();
    } catch(error) {
        console.log('error auto play:' + error);
    }
}

// Cleanup Video Element
function cleanupRemoteVideoElement(video) {
    video.pause();
    video.srcObject = null;
    remoteVideosContainer.removeChild(video);
}

// Get Remote Video Element
function getRemoteVideoElement(uuid) {
    let video = remoteVideos[uuid];
    delete remoteVideos[uuid];
    return video;
}

// ------------------ Handler for Peer Connections -----------------
function getConnectionCount() {
    return peerConnections;
}

function isConnectedWith(id) {
    if (peerConnections[id]) {
        return true;
    } else {
        return false;
    }
}

function addConnection(id, peer) {
    peerConnections[id] = peer;
}

function getConnection(id) {
    return peerConnections[id];
}

function deleteConnection(id) {
    delete peerConnections[id];
}