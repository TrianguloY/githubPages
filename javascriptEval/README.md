### JavascriptEval:

#### Url: 

[https://trianguloy.github.io/githubPages/javascriptEval/javascriptEval.html](https://trianguloy.github.io/githubPages/javascriptEval/javascriptEval.html)

#### Description:


Enter any script in the textbox and press the Eval button. The script will run in the page.
That's all.


Why? Let me explain. 
Sometimes you need to report a bug when using a specific script (for example an explot for a undiscovered attack) and you need an online page so others can test it directly. Most of the times the script is easy and short, but still you need a server to publish it, and not all people have a server.

'Oh! I know. I'll use one of the thousands of editors available on the web.'
Yes, that's a solution...except when you discover that all of them (or maybe the 99%, but I didn't find that 1%) use an iframe or similar to encapsulate the code/html/css. This is done either for convenience or simply to avoid problems between the host page and the running code. 
However this has problems, because the entered code is running constrained inside a container, where some functions/properties are not available. For example. You can't change the window title: [`document.title = "my title"`](https://trianguloy.github.io/githubPages/javascriptEval/javascriptEval.html?document.title%20=%20%22my%20title%22).

Basically by using eval the entered code is run directly on the page. This can lead to serious consecuences if the code is malicious or uses an exploit ... however that's precisely why it was created!

You have full control over the page, you can even delete the editor itself: [`document.body.removeChild(document.getElementById('javascriptEval'))`](https://trianguloy.github.io/githubPages/javascriptEval/javascriptEval.html?document.body.removeChild(document.getElementById('javascriptEval'))) and remember you can add buttons or other things too [`let btn = document.createElement('button'); btn.innerHTML = 'Press me'; btn.onclick = ()=> alert("Hello"); document.body.appendChild(btn);`](https://trianguloy.github.io/githubPages/javascriptEval/javascriptEval.html?let%20btn%20=%20document.createElement('button');%20btn.innerHTML%20=%20'Press%20me';%20btn.onclick%20=%20()=%3E%20alert(%22Hello%22);%20document.body.appendChild(btn);). This is also the reason why the page is so simple and dumb. It was designed as a way to share scripts that can be run directly. That's why there are only three buttons: run (eval), share, and info.
