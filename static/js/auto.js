fetch('/autocomplete_data')
      .then(function (response) {
          return response.json();
      }).then(function (data) {
          console.log('GET response:');
          
          let availableTags = data;
          //console.log(availableTags);

          $( function() {        
            $( "#tags" ).autocomplete({
              source: availableTags
            });
          } );
      });

