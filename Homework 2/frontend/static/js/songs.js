getDownloads = function() {
    fetch('/songs').then(function (response) {
        return response.text();
    }).then(function (html) {
        let songs_div = document.getElementById("songs");
        songs_div.innerHTML = html;
        console.log("got songs data");
    }).catch(function (err) {
        // There was an error
        console.warn('Something went wrong.', err);
    });
}

var intervalId = window.setInterval(function(){
  getDownloads();
}, 5000);