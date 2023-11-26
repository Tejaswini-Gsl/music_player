

// function goToArtist() {
//   window.location.href = '/playlist';
// }

// playlists.js

// async function getPlaylists() {
//   const response = await fetch('/playlist');
//   return response.json();
// }

// document.addEventListener('DOMContentLoaded', async () => {
//   const playlists = await getPlaylists();
//   displayPlaylists(playlists); 
// });

// function displayPlaylists(playlists) {
//   // insert playlists into DOM
// }



// var coll = document.getElementsByClassName("collapsible");
// var i;

// for (i = 0; i < coll.length; i++) {
//   coll[i].addEventListener("click", function() {
//     this.classList.toggle("active");
//     var content = this.nextElementSibling;
//     if (content.style.maxHeight){
//       content.style.maxHeight = null;
//     } else {
//       content.style.maxHeight = content.scrollHeight + "px";
//     } 
//   });
// }

// script.js

// document.getElementById('playlistsButton').addEventListener('click', function() {
//   const playlistContent = document.getElementById('playlistContent');
  
//   // Clear existing content
//   playlistContent.innerHTML = '';

//   // Fetch playlists and update the content
//   fetch('/get_playlists')  // Assuming this route returns playlist data
//       .then(response => response.json())
//       .then(data => {
//           const existingPlaylists = data.playlists;

//           // Add existing playlists to the content
//           existingPlaylists.forEach(playlist => {
//               const playlistLink = document.createElement('a');
//               playlistLink.href = `#`;  // Update with the appropriate link
//               playlistLink.innerText = playlist.playlist_name;
//               playlistContent.appendChild(playlistLink);
//           });

//           // Add other content as needed
//           const createPlaylistLink = document.createElement('a');
//           createPlaylistLink.href = '/create_playlist';
//           createPlaylistLink.innerText = 'Create New Playlist';
//           playlistContent.appendChild(createPlaylistLink);

//           const loremParagraph = document.createElement('p');
//           loremParagraph.innerText = 'Lorem ipsum...';
//           playlistContent.appendChild(loremParagraph);
//       })
//       .catch(error => console.error('Error fetching playlists:', error));
// });