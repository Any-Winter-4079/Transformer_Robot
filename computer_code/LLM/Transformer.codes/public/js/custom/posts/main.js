document.addEventListener('DOMContentLoaded', function () {
  const codeElements = document.querySelectorAll('[class*="language-"]');
    if (codeElements.length > 0) {
        // Load Prism.js dynamically if code elements are found
        loadScript('../js/posts/prism.js', function() {
            console.log('Prism.js loaded successfully!');
        });
  }
  let topButtons = document.getElementsByClassName('topButton');

  for (let btn of topButtons) {
      let supportEmail = btn.getAttribute('data-support-email');
      // let youtubeUrl = btn.getAttribute('data-youtube-url');
      let githubUrl = btn.getAttribute('data-github-url');

      if (supportEmail) {
          btn.addEventListener('click', function(event) {
              // Prevent the default action
              event.preventDefault();

              // Open an email client
              window.location.href = "mailto:" + supportEmail;
          });
      } else {
          // If no supportEmail, then we check for the other URLs
          if (githubUrl) {
              btn.addEventListener('click', function(event) {
                  // Prevent the default action
                  event.preventDefault();

                  // Open Github in a new tab
                  window.open(githubUrl, '_blank');
              });
          } 
        //   if (youtubeUrl) {
        //       btn.addEventListener('click', function(event) {
        //           // Prevent the default action
        //           event.preventDefault();

        //           // Open Youtube in a new tab
        //           window.open(youtubeUrl, '_blank');
        //       });
        //   }
      }
  }
}, false);
