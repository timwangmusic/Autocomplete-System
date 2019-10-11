/*An array some words at random from Game Of thrones:*/
function processWords()
{
    var fs = require('fs');
    var words = "";
    fs.readFile("./gotchars.txt", 'utf-8', function read(err, text) {
        if (err) {
            throw err;
        }
        if (text){
            words = text.split('\n');
        }
        console.log(JSON.stringify(words));
        return words
    });
}

function processFile() {
    processWords();
}

processFile();
