function to_date_string(date) {
    if (! date) {
        return "";
    }
    let d = new Date(date);
    return d.toLocaleDateString("de", { year:"numeric", month:"short", day:"numeric"});
}
