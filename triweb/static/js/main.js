function any_to_date(date_str) {
    ts = Date.parse(date_str);
    if (!ts) {
        return null;
    }
    return new Date(ts);
}

function to_date_string(date, weekday=false) {
    if (! date) {
        return "";
    }
    let d = new Date(date);
    let opts = { year:"numeric", month:"short", day:"numeric"};
    if (weekday) {
        opts.weekday = "short";
    }
    return d.toLocaleDateString("de", opts);
}

function to_datetime_string(date) {
    if (! date) {
        return "";
    }
    let d = new Date(date);
    return d.toLocaleTimeString("de", { year:"numeric", month:"short", day:"numeric"});
}


