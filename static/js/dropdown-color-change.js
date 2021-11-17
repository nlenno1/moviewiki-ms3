function initializeSelectElementColorChange() {
    let elementList = document.getElementsByTagName('select'); // find select elements
    for (let i = 0; i < elementList.length; i++) { // add change event listener to all
        elementList[i].addEventListener("change", function () {
            this.classList.add("text-black"); // change text color
        });
    }
}

$('document').ready (function () {
    initializeSelectElementColorChange();
});

