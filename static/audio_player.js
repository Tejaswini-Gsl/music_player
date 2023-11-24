function playSong(id) {
    let audio = document.getElementById('${id}');
    audio.play();
  }
  
  function pauseSong(id) {
    let audio = document.getElementById('${id}');
    audio.pause(); 
  }

// let audio = document.getElementById('audio');
// audio.muted = true;
// audio.play();