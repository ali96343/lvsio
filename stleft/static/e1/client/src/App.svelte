<script>

// 1
 let message = '';
 let src = '';
 async function getName() {
     let thisMessage = message;
     let res = await fetch(E1_MESSAGE + `?name=${message}`);
     //let res = await fetch('http://localhost:8000/left/message_e1' + `?name=${message}`);
     let message_received = await res.text();
     if (res.ok && thisMessage == message) {
             src = message_received;
     }
  }

// 2

  let count = 0;
  function incCount() {
    count++;
  }
  function decCount() {
    count--;
  }


// 3

let rand = -1;
  function getRand() {
    fetch(E1_RANDOM)
      .then(d => d.text())
      .then(d => (rand = d));
  }

//4

    import { onMount } from "svelte";

    const apiURL = E1_JSON;
    // const apiURL = "https://jsonplaceholder.typicode.com/todos";
    let data = [];

    onMount(async function() {
        const response = await fetch(apiURL);
        data = await response.json();
    });

</script>

<main>

<!-- 1 -->

<p>p4w_ctrl_param: {CTRL_PARAM}</p>
<h1>Received Message: {src}!</h1>
<input type="text" placeholder="enter your name" bind:value={message} />
<button on:click={getName}>Send Message</button>


<p> Compile-1 <a href="https://lihautan.com/compile-svelte-in-your-head-part-1/">Svelte compile-1</a> </p>
<p> Compile-2 <a href="https://lihautan.com/compile-svelte-in-your-head-part-2/">Svelte compile-2</a> </p>
<p> Compile-3 <a href="https://lihautan.com/compile-svelte-in-your-head-part-3/">Svelte compile-3</a> </p>

<p>
    Visit the <a href="https://www.koderhq.com/tutorial/svelte/">Svelte tutorial</a> how to works Svelte apps.
  </p>

<!-- 2 -->

<h1>The count is {count}</h1>
<button on:click={incCount}>Increment count</button>
<button on:click={decCount}>Decrement count</button>

<!-- 3 -->

<h1>Your random number is {rand}!</h1>
<button on:click={getRand}>Get a random number</button>

<!-- 4 note -->
<pre>
alias newclient="npx degit sveltejs/template client && cd client && npm i"
alias rudev="npm run dev"
</pre>

<div>
<h1>e1_json</h1>
{#each data as item }
            <div>
                <p> {item.a} {item.b}</p>
            </div>
        {/each}
</div>
</main>


<style>
  main {
    text-align: left;
    padding: 1em;
    max-width: 240px;
    margin: 0 auto;
  }

  h1 {
    color: #ff3e00;
    text-transform: uppercase;
    font-size: 1.2em;
    font-weight: 100;
  }

  @media (min-width: 640px) {
    main {
      max-width: none;
    }
  }
</style>


