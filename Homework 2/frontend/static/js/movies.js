moviesSelect = function() {
    let media = document.getElementById("mediaSelect").value;
    if (media !== "Movie" && media !== "All Content" && media !== "TV Show" && media !== "Person") {
        media = "All Content";
    }
    if (media === "TV Show") media = "tv";
    else if (media === "All Content") media = "all";
    media = media.toLowerCase();

    let timerange = document.getElementById("timerangeSelect").value;
    if (timerange !== "Last 24 Hours" && timerange !== "Last Week") {
        timerange = "Week";
    }
    if (timerange === "Last 24 Hours") timerange = "day";
    else if (timerange === "Last Week") timerange = "week";
    timerange = timerange.toLowerCase();

    fetch('/trending/' + media +'/' + timerange).then(function (response) {
        return response.text();
    }).then(function (html) {
        let movies_div = document.getElementById("movies");
        movies_div.innerHTML = html;
        console.log("got " + media + " data");
    }).catch(function (err) {
        // There was an error
        console.warn('Something went wrong.', err);
    });
}

searchContent = function() {
    event.preventDefault();
    let search = document.getElementById("search").value;
    console.log("searching for ");

    fetch('/search/' + search).then(function (response) {
        return response.text();
    }).then(function (html) {
        let movies_div = document.getElementById("movies");
        movies_div.innerHTML = html;
        console.log("got " + search + " data");
    }).catch(function (err) {
        // There was an error
        console.warn('Something went wrong.', err);
    });
}

moviesSelect();
