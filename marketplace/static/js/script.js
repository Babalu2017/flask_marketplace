document.addEventListener('DOMContentLoaded', function () {
  let sidenav = document.querySelectorAll('.sidenav');
  var instances = M.Sidenav.init(sidenav);

  let modal = document.querySelectorAll('.modal');
  var instances = M.Modal.init(modal);

  let datepicker = document.querySelectorAll(".datepicker");
  M.Datepicker.init(datepicker, {
    format: "dd mmmm, yyyy",
    i18n: { done: "Select" }
  });

  let selects = document.querySelectorAll("select");
  M.FormSelect.init(selects);

  let collap = document.querySelectorAll('.collapsible');
  M.Collapsible.init(collap);

  let chips = document.querySelectorAll('.chips');
  M.Chips.init(chips);

  $(".dropdown-trigger").dropdown();


 

});




