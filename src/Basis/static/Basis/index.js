document.addEventListener('DOMContentLoaded', function () {
  var searchBtn = document.querySelector('.search-btn');
  if (!searchBtn) return;

  searchBtn.addEventListener('click', function (e) {
    var inputs = document.querySelectorAll('.search-input');
    var vals = Array.from(inputs).map(function (i) { return i.value.trim(); }).filter(Boolean);
    if (vals.length === 0) {
      alert('Bitte Suchbegriffe eingeben.');
    } else {
      alert('Suche nach: ' + vals.join(' | '));
    }
  });
});
