/*
  NOTE: to update the running production instance of this code:
  1) Go to File => Manage versions and add a new version.
  2) Then go to Publish, select the new version number, and click update.
*/

var INTENTS = [" implement"," deprecate"," ship"," remove"];

function doPost(request) {
  var ss = SpreadsheetApp.openById("0AjGgk26K1Cc-dHJKNGtlLVlmSGRIYVR3LVRGYnVCRVE");
  var sheet = ss.getSheetByName("DATA");
  var lastRow = sheet.getLastRow();
  var currentRow = lastRow + 1;
  Logger.log("Intent received!");
  Logger.log(new Date());
  sheet.getRange(currentRow, 1, 1).setValue(request.parameter); // Put raw data in first column on next available row.
  sheet.getRange(currentRow, 2, 1).setValue(Utilities.formatDate(new Date(), "PST", "MM/dd/yyyy"));
  sheet.getRange(currentRow, 3, 1).setValue(request.parameter.sender); // Sender
  sheet.getRange(currentRow, 4, 1).setValue(getIntentType(request.parameter.subject));
  sheet.getRange(currentRow, 5, 1).setValue("=HYPERLINK(\"" + request.parameter.link + "\", \"" + getSubject(request.parameter.subject) + "\")");
}

function getIntentType(subject) {
  var lowerCaseSubject = subject.toLowerCase();
  var intentType = "";
  for (var i = 0; i < INTENTS.length; i++)
    if (lowerCaseSubject.indexOf(INTENTS[i]) >= 0)
      intentType += (intentType.length == 0) ? 
        capitalizeFirstLetter(INTENTS[i].trim()) : " and " + INTENTS[i].trim();
  return intentType;
}

function getSubject(subject) {
  var lastIntentTypeEndIndex = -1;
  var curIntentTypeEndIndex = -1;
  var lowerCaseSubject = subject.toLowerCase();
  for (var i = 0; i < INTENTS.length; i++) {
    curIntentTypeEndIndex = lowerCaseSubject.indexOf(INTENTS[i]) + INTENTS[i].length;
    if (curIntentTypeEndIndex >= lastIntentTypeEndIndex)
      lastIntentTypeEndIndex = curIntentTypeEndIndex;
  }
  if (lastIntentTypeEndIndex == -1) Logger.log("Intent type string not found.");
  // If there's a colon, the "+1" should get rid of it.
  var trimmedSubject =  subject.substring(lastIntentTypeEndIndex+1).trim();
  // Double quotes don't play nice with Google Spreadsheets.
  return trimmedSubject.replace(/"/g, "'");
}

function capitalizeFirstLetter(string) {
    return string.charAt(0).toUpperCase() + string.slice(1);
}
