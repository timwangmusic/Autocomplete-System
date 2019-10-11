## Dependencies that you need to install to run the auto_sense.html file

 + Install node.js
 + Install npm
 + Install the required npm packages, 

 ```
 (base) Sandeeps-MacBook-Pro:templates sandeepanand$ npm list -g --depth=0
/usr/local/lib
├── browserify@16.5.0
├── gulp-cli@2.2.0
└── npm@6.11.3
```

### After installation of the above just run from cmd as below

```
open -a "firefox" auto_sense.html
open -a "Google Chrome" auto_sense.html
```

### What are the files that you are seeing within the `templates` folder
 + auto_sense.html - this is the file that forms the skeleton to run Auto sense on the Autocomplete output
 + gotchars.txt - this file is a demo file that contains the words to input to the auto_sense.html, this acts like a database currently, the plan is once the skeleton is integrated then we can take this out and put the input as the redis cache
 + readchars.js - this file runs independently to extract the words from the file `gotchars.txt`

### Issue that I facing 
+ Currently `words` inside the `auto_sense.html` file is given as fixed value, I want to call the function `readchars.js` within the html file and which is returning words, which is not happening rite now -- we will need to figure this out ? 