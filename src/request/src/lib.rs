extern crate cpython;

use std::env;
use curl::easy::{Easy, List};
use cpython::{Python, PyDict, PyResult, py_module_initializer, py_fn};

fn request(py: Python, url: &str, method: &str, render: bool, user_agent: &str, use_proxy: bool) -> PyResult<PyDict> {
    let request_url;
    let pyresult = PyDict::new(py);
    // This code block is specific to the use of scrapeAPI
    // and if you want to use another API to render web pages
    // you should change how it's implemented
    if render {
        let api_key;
        let mut do_render = "true";
        match env::var("API_KEY") {
            Ok(value) => api_key = value,
            Err(_e) => api_key = "none".to_string(),
        }

        if use_proxy {
            do_render = "false";
        }

        request_url = format!("http://api.scraperapi.com/?api_key={API_KEY}&url={URL}&render={RENDER}", 
                            API_KEY = api_key,
                            URL = url,
                            RENDER = do_render);
    } else {
        request_url = url.to_string();
    }

    if method.to_lowercase() == "get" {
        let mut data = Vec::new();
        let mut handle = Easy::new();
        
        let mut header = List::new();
        header.append("Accept: text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9").unwrap();
        header.append("Accept-Language: en-US,en;q=0.9,pt;q=0.8").unwrap();
        header.append("Cache-Control: no-cache").unwrap();
        header.append("Connection: keep-alive").unwrap();
        header.append("Pragma: no-cache").unwrap();
        header.append("Sec-Fetch-Dest: document").unwrap();
        header.append("Sec-Fetch-Mode: navigate").unwrap();
        header.append("Sec-Fetch-Site: none").unwrap();
        header.append("Sec-Fetch-User: ?1").unwrap();
        header.append(user_agent).unwrap();

        handle.url(&request_url).unwrap();
        handle.follow_location(true).unwrap();
        handle.http_headers(header).unwrap();
        handle.perform().unwrap();
        handle.get(true).unwrap();
        {
            let mut transfer = handle.transfer();
            transfer.write_function(|new_data| {
                data.extend_from_slice(new_data);
                Ok(new_data.len())
            }).unwrap();
            transfer.perform().unwrap();
        }
        pyresult.set_item(py, "content", String::from_utf8_lossy(&data));
        pyresult.set_item(py, "status_code", handle.response_code().unwrap());
    }
    // TODO:
    // 1: Implement POST method right after this if statement

    Ok(pyresult)
}

py_module_initializer!(librequest, initlibrequest, PyInit_request, |py, m | {
    m.add(py, "__doc__", "This module is implemented in Rust")?;
    m.add(py, "request", py_fn!(py, request(url: &str, method: &str, render: bool, user_agent: &str, use_proxy: bool)))?;
    Ok(())
});