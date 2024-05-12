// context_menu.js

document.addEventListener("DOMContentLoaded", function () {
    const documents = document.querySelectorAll(".document");
    const contextMenu = document.getElementById("contextMenu");
    const renameAction = document.getElementById("renameAction");
    const deleteAction = document.getElementById("deleteAction");
  
    function actionURLS(documentId) {
      if (renameAction && deleteAction) {
        renameAction.href = "/rename/" + documentId;
        deleteAction.href = "/delete/" + documentId;
        console.log(documentId);
      } else {
        console.log("Null DocID");
      }
    }
  
    function displayContextMenu(event, documentId) {
      event.preventDefault();
  
      var contextMenu = document.getElementById("contextMenu");
  
      actionURLS(documentId);
      console.log("Selected Document ID:", documentId);
      contextMenu.style.display = "block";
      contextMenu.style.left = event.pageX + "px";
      contextMenu.style.top = event.pageY + "px";
  
      document.addEventListener("click", function () {
        contextMenu.style.display = "none";
      });
    }
    documents.forEach(function (document) {
      document.addEventListener("contextmenu", function (event) {
        const documentId = document.dataset.documentId;
        displayContextMenu(event, documentId);
      });
  
      document.addEventListener("click", function (event) {
        // Retrieve document_id from data attribute
        const documentId = document.dataset.documentId;
  
        // Output document_id to console
        console.log("Selected Document ID:", documentId);
  
        if (document.classList.contains("selected")) {
          document.classList.remove("selected");
        } else {
          documents.forEach(function (doc) {
            doc.classList.remove("selected");
          });
          document.classList.add("selected");
        }
      });
    });
  });
  