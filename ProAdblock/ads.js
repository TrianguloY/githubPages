/*
 * Pro Adblock
 * https://trianguloy.github.io/githubPages/ProAdblock/main.html
 */

var domString = `<div class="bottomAd" style="padding: 10px; background: #500000; text-align: center; font-weight: bold; color: #fff; border-radius: 5px;">
(!) You are not using an adblocker, you are surfing the web full of ads (and companies may be using your data to target and/or track you). 
<br>Consider using an adblock, they are available for almost all commercial browsers and will remove almost all ads from the web!
</div>`;

var div = document.createElement('div');
div.innerHTML = domString;
var script = document.scripts[document.scripts.length - 1];
script.parentElement.insertBefore(div.firstChild, script); 