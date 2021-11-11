function initializeSelectElementColorChange() {
    elementList = document.getElementsByTagName('select');
    for (let i = 0; i < elementList.length; i++) {
        elementList[i].addEventListener("change", function () {
            this.classList.add("text-black");
        });
    }
}

$('document').ready (function () {
    initializeSelectElementColorChange();
})

