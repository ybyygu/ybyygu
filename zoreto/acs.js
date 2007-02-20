function detectWeb(doc, url) {
	var re = new RegExp('^http://pubs\.acs\.org/cgi-bin/(article|abstract)\.cgi/', 'i');
	if(re.test(doc.location.href)) {
		return "journalArticle";
	}
}
