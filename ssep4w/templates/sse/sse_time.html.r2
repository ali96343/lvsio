[[extend 'layout.html']]

<button type="button" onclick="window.open(  window.location.href  );">new tab</button>
<button id="breaj_but" type="button" onclick="window.location.reload(true);">reload</button>

<p>./py4web.py run apps --watch=off -s wsgirefThreadingServer</p>
<p id='gen_id'></p>
<p id="event_id"></p>
<p id="time"></p>
<p id="value"></p>


<script>
 function(data_url) {

   let lastId = 0;
   let data_url_id = data_url  + '?lastId=' + lastId.toString();

   let source = new EventSource( data_url_id  );
   const messageHandler  = function (e) {
       const fs= '1.4em';
       const data = JSON.parse(e.data);

       document.getElementById("time").innerHTML = data.time;
       document.getElementById("time").style.fontSize = fs;

       document.getElementById("value").innerHTML = 'random: ' +  data.value;
       document.getElementById("value").style.fontSize = fs;

     
       lastId = e.lastEventId;
       data_url_id = data_url  + '?lastId=' + lastId.toString();

       document.getElementById("event_id").innerHTML = data_url_id ; //   e.lastEventId;
       document.getElementById("event_id").style.fontSize = fs;

   }
   source.onmessage = messageHandler; 

   source.addEventListener("generator_start", function(e) {
       const data = JSON.parse(e.data);
       document.getElementById("gen_id").innerHTML = 'Generator id: ' + data.gen_id ;
   });

//   source.onerror = function(e) {
//           console.error("EventSource failed:", e);
//           if (e.readyState == EventSource.CLOSED) {
//            console.log('sse bye! connectioni closed!');
//            }
//   };

   source.addEventListener("open", (event) => {
         // Prints the information about an event
         console.log('open connection! ',event);
   });



const sourceErrorHandler = function(event){
    let txt;
    switch( event.target.readyState ){
        case EventSource.CONNECTING:
            txt = 'Reconnecting... 111' + data_url_id;
            break;
        case EventSource.CLOSED:
            txt = 'Reinitializing...222'+ data_url_id;
            source = new EventSource(data_url_id);
            source.onerror = sourceErrorHandler;
            source.onmessage = messageHandler; 
            break;
    }
    console.log(txt);
}

source.onerror = sourceErrorHandler;

// https://stackoverflow.com/questions/32079582/server-sent-events-how-do-you-automatically-reconnect-in-a-cross-browser-way

// https://stackoverflow.com/questions/24564030/is-an-eventsource-sse-supposed-to-try-to-reconnect-indefinitely

}( "[[=stream_url ]]"  )


</script>


<script>

// https://stackoverflow.com/questions/24564030/is-an-eventsource-sse-supposed-to-try-to-reconnect-indefinitely


! function (data_url) {
  
  let reconnectFrequencySeconds = 1;
  let evtSource;

  let lastId = 0;
  let data_url_id = data_url  + '?lastId=' + lastId.toString();
  
  // Putting these functions in extra variables is just for the sake of readability
  const waitFunc = function() { return reconnectFrequencySeconds * 1000 };
  const tryToSetupFunc = function() {
      setupEventSource();
      reconnectFrequencySeconds *= 2;
      if (reconnectFrequencySeconds >= 64) {
          reconnectFrequencySeconds = 64;
      }
  };
  
  const reconnectFunc = function() { setTimeout(tryToSetupFunc, waitFunc()) };
  
  function setupEventSource() {
      evtSource = new EventSource( data_url_id  ); 
      evtSource.onmessage = function(e) {
        console.log(e);

       const fs= '1.4em';
       const data = JSON.parse(e.data);

       document.getElementById("time").innerHTML = data.time;
       document.getElementById("time").style.fontSize = fs;

       document.getElementById("value").innerHTML = 'random: ' +  data.value;
       document.getElementById("value").style.fontSize = fs;


       lastId = e.lastEventId;
       data_url_id = data_url  + '?lastId=' + lastId.toString();

       document.getElementById("event_id").innerHTML = data_url_id ; //   e.lastEventId;
       document.getElementById("event_id").style.fontSize = fs;


      };

      evtSource.onopen = function(e) {
        reconnectFrequencySeconds = 1;
        console.log('open connection! ',e);
        console.log('reconnectFrequencySeconds:  ',reconnectFrequencySeconds);
      };

      evtSource.onerror = function(e) {
        evtSource.close();
        reconnectFunc();
      };

      // user events 

      evtSource.addEventListener("generator_start", function(e) {
          const data = JSON.parse(e.data);
          document.getElementById("gen_id").innerHTML = 'Generator id: ' + data.gen_id ;
      });


  }
  
  setupEventSource();
  
}( "[[=stream_url ]]"  )

</script>
