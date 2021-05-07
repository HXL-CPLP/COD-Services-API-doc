#!/usr/bin/env node
// Trivia:
// - "displicandum"
//   - https://en.wiktionary.org/wiki/displico#Latin
//   - English, "deploy", "deployment"
//     - https://en.wiktionary.org/wiki/deploy
// - 'gh-pages'
//   - https://www.npmjs.com/package/gh-pages
//   - https://pages.github.com/


// npm gh-pages ______________________________________________________________
// @see https://www.npmjs.com/package/gh-pages
// npm install -g gh-pages

// Were in branch main at this point, publishing files to branch gh-pages folder docs/
//    gh-pages --src '**/*' --dest '.' --branch gh-pages --user 'HXL-CPLP bot <no-reply@etica.ai>' --no-push --no-history

// TODO: consider use --before-add 
//       https://www.npmjs.com/package/gh-pages#optionsbeforeadd

// ./systema/programma/displicandum-gh-pages.js

var ghpages = require('gh-pages');

// console.log('Hello world!');

// var callback = console.log

ghpages.publish(
    // We're using root folder of HXL-CPLP/Auxilium-Humanitarium-API/ as source
    './',
    {
        // Branch to publish: gh-pages
        branch: 'gh-pages',

        // Directory to publish: docs/
        dest: 'docs/',

        // Copy .dotfiles to dest?: false
        dotfiles: false,

        // Only add, never remove from dest? : false
        add: false,

        // Remove files on dest before commit
        remove: "node_modules/",

        // Push to target repository
        push: false,

        // Keep history from other pages
        // Note: this would waste too much resources and branch main already
        //       have information to re-recreate pages
        history: false,

        // Avoid showing repository URLs or other information in errors.
        // silent: true,

        // Repo to publish (if not same local repo): (ommited)
        // repo: 'https://example.com/other/repo.git',

        // beforeAdd makes most sense when `add` option is active
        // Assuming we want to keep everything on the gh-pages branch
        // but remove just `some-outdated-file.txt`
        // async beforeAdd(git) {
        //     return git.rm('./some-outdated-file.txt');
        // },

        // Git remote to publish (if not same local repo): (ommited)
        // remote: 'upstream',

        message: 'Displicandum gh-pages' + (new Date).toISOString() + ': Auxilium Humanitarium API documentōrum',

        user: {
            name: 'HXL-CPLP bot',
            email: 'no-reply@etica.ai'
        }
    },
    function (err) {
        console.log(err)
    }
);

// // ghpages.publish('dist', {
// publish('./', {
//     branch: 'gh-pages',
//     // repo: 'https://example.com/other/repo.git'
// }, callback);