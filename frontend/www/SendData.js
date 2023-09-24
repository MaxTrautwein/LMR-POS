
const ServerAddress = "http://127.0.0.1:5000"
function httpGetAsync(theUrl, callback) {
    let xmlHttp = new XMLHttpRequest();
    xmlHttp.onreadystatechange = function () {
        if (xmlHttp.readyState == 4 && xmlHttp.status == 200)
            callback(xmlHttp.responseText);
    }
    xmlHttp.open("GET", theUrl, true); // true for asynchronous
    xmlHttp.send(null);
}

function PostJson(jsonData,url,callback = __DebugCallback){
    let data = JSON.stringify(jsonData);
    fetch(url, {
        method: 'POST',
        headers: {
            'Accept': 'application/json',
            'Content-Type': 'application/json'
        },
        body: data
    })
        .then(response => response.json())
        .then(response => callback(response));

}

function __DebugCallback(json){
    console.log(JSON.stringify(json));
}