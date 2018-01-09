function check() {
  gstin = (document.getElementsByName('gstin')[0].value)
  console.log(!(gstin[0] == '1' && gstin[1] == '9'));

  if (gstin == "") {
    // gstin is empty
    if (!document.getElementsByName('ur')[0].checked) {
      // Unregistered unchecked
      showMessage("No GSTIN provided", `Please Provide GSTIN <br />OR <br /> Select Unregistered Dealer`);
      return false;
    } else {
      // Unregistered ledger
      if (document.getElementsByName('pos')[0].value == '') {
        // POS not given
        //console.log('No POS');
        showMessage("No Place of Supply Provided",'Please Provide Place of Supply');
        return false;
      }
      return true;
    }
  } else {
    // gstin not empty
    document.getElementsByName('ur')[0].checked = false
    document.getElementsByName('pos')[0].value = gstin[0]+gstin[1]
  }
  gstinwocd = gstin.substring(0, gstin.length - 1).split("")
  cpChars = "0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ".split("")

  factor = 2
  sum = 0
  checkCodePoint = 0
  mod = cpChars.length

  for (i = gstinwocd.length - 1; i >= 0; i--) {
    codePoint = -1
    for (j = 0; j < cpChars.length; j++) {
      if (cpChars[j] == gstinwocd[i]) {
        codePoint = j;
      }
    }
    digit = parseInt(factor * codePoint)
    factor = (factor == 2) ? 1 : 2
    digit = parseInt(digit / mod) + parseInt(digit % mod)
    sum += parseInt(digit)
  }
  checkCodePoint = parseInt((mod - (sum % mod)) % mod)
  checkdigit = cpChars[checkCodePoint]
  //console.log()
  console.log(checkdigit);
  if (checkdigit != gstin[gstin.length - 1]) {

    showMessage("GSTIN Checksum Mismatch", "Recheck GSTIN")
    return false;
  }
  return true;

}
