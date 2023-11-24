// Add a new JavaScript file (scripts/slideshow.js) for slideshow functionality

let slideIndexTop = 0;

function showSlidesTop() {
    let slidesTop = document.getElementsByClassName("slide");
    for (let i = 0; i < slidesTop.length; i++) {
        slidesTop[i].style.display = "none";
    }
    slideIndexTop++;
    if (slideIndexTop > slidesTop.length) {
        slideIndexTop = 1;
    }
    slidesTop[slideIndexTop - 1].style.display = "block";
    setTimeout(showSlidesTop, 3000); // Change slide every 3 seconds
}

document.addEventListener("DOMContentLoaded", function () {
    showSlidesTop();
});
