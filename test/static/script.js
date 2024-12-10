// Add event listeners to artist images
document.querySelectorAll('.artist-image').forEach(item => {
    item.addEventListener('click', event => {
        // Get the artist ID from the data attribute
        const artistId = item.dataset.artistId;
        
        // Send an AJAX request to Flask to fetch artist songs
        fetch(`/artist/${artistId}`)
            .then(response => response.json())
            .then(data => {
                // Update the table with the fetched songs
                const tableBody = document.querySelector('.songs-list table tbody');
                tableBody.innerHTML = ''; // Clear existing table rows
                
                data.songs.forEach(song => {
                    const row = `<tr>
                                    <td>${song.album}</td>
                                    <td>${song.name}</td>
                                    <td>${song.genre}</td>
                                    <td>${song.duration}</td>
                                </tr>`;
                    tableBody.innerHTML += row;
                });
            })
            .catch(error => {
                console.error('Error:', error);
            });
    });
});


