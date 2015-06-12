var modules = require(__dirname + '/modules.js');
var async = require('async');
var fs = require('fs');

var logFileLoc = 'C:\\Users\\administrator.NPLATL\\Desktop\\Server Side Scripts\\DatWatcher\\Logs\\errorLog.txt';
var errorEmails = 'smccoy@nationalparcel.com, dgriffin@nationalparcel.com';
var pathToFtp = 'F:\\mailDats';
var pathToDatFolder = 'c:\\DATData';

async.waterfall([
    function getZipFiles(done){
        fs.readdir(pathToFtp, function(err, files){
            done(null, files);
        })
    },
    function allowOnlyZips(files, done){
        files = files.filter(function(file){
            if(file.toLowerCase().indexOf('.zip') != -1){
                return true;
            } else {
                return false;
            }
        });
        done(null, files);
    },
    function runEachUpload(files, done){
        async.each(files, function(file, unZipDone){
            modules.unZip(file, pathToDatFolder, function)
        })
    }
])