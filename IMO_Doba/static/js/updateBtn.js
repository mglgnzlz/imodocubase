// update_btn.js

document.getElementById("update-btn").addEventListener("click", function () {
    // Send an AJAX request to the Django view
    var xhr = new XMLHttpRequest();
    xhr.open("GET", '{% url "doc_update" %}', true);
    xhr.onload = function () {
      if (xhr.status == 200) {
        alert("Data updated successfully");
      } else {
        alert("Failed to update data");
      }
    };
    xhr.send();
  });
  