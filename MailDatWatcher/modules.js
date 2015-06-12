var nodemailer = require('nodemailer');
var admZip = require('adm-zip');
var async = require('async');

exports.sendEmail = function(addresses, subject, msg){
    var transporter = nodemailer.createTransport({
        service: 'Hostway',
        auth: {
            user: 'networkalerts@nationalparcel.com',
            pass: '2Simplex'
        }
    });

    var mailOptions = {
        from: 'DatFileError@nationalparcel.com',
        to: addresses,
        subject: subject,
        text: msg
    };

    transporter.sendMail(mailOptions, function(error, info){
        if(error){
            _writeToLog(logPath, error);
        }
    });
};

exports.unZip = function(file, datLocation, callback){
    var cmsFile, hdrFile;
    var zip = new admZip(file);
    var zipEntries = zip.getEntries();

    async.each(zipEntries, function(zipEntry, done){
        if(zipEntry.indexOf('.hdr') != -1){
            hdrFile = zipEntry;
        }
        if(zipEntry.indexOf('.cms') != -1){
            cmsFile = zipEntry;
        }
        done(null);
    }, function(err){
        zip.extractEntryTo(hdrFile, datLocation);
        zip.extractEntryTo(cmsFile, datLocation);
        callback(hdrFile, cmsFile);
    })
}

function _writeToLog(path, msg){

};