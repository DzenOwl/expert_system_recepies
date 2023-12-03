window.onbeforeunload = function () {
    localStorage.setItem('facts', JSON.stringify(vueApp.facts));
    localStorage.setItem('rules', JSON.stringify(vueApp.rules));
}