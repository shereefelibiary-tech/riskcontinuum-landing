/* Open a directly linked question using its fixed, public HTML id. */
(function () {
  "use strict";
  function openQuestion() {
    var question = document.getElementById(location.hash.slice(1));
    if (question && question.tagName === "DETAILS") question.open = true;
  }
  openQuestion();
  addEventListener("hashchange", openQuestion);
  var beforePrint = [];
  addEventListener("beforeprint", function () {
    beforePrint = Array.from(document.querySelectorAll("details"), function (question) {
      var state = { question: question, open: question.open };
      question.open = true;
      return state;
    });
  });
  addEventListener("afterprint", function () {
    beforePrint.forEach(function (state) { state.question.open = state.open; });
    beforePrint = [];
  });
}());
