import numpy as np
import pandas as pd
import streamlit as st

st.write(
    f'<span style="font-size: 78px; line-height: 1">🐱</span>',
    unsafe_allow_html=True,
)

"""
# Static file serving
"""

st.caption(
    "[Code for this demo](https://github.com/streamlit/static-file-serving-demo/blob/main/streamlit_app.py)"
)

"""
Streamlit 1.18 allows you to serve small, static media files via URL. 

## Instructions

- Create a folder `static` in your app's root directory.
- Place your files in the `static` folder.
- Add the following to your `config.toml` file:

```toml
[server]
enableStaticServing = true
```

You can then access the files on `<your-app-url>/app/static/<filename>`. Read more in our 
[docs](https://docs.streamlit.io/library/advanced-features/static-file-serving).

## Examples

You can use this feature with `st.markdown` to put a link on an image:
"""

with st.echo():
    st.markdown("[![Click me](./app/static/join.png)](https://streamlit.io)")

"""
Or you can use images in HTML or SVG:
"""

with st.echo():
    st.markdown(
        '<img src="./app/static/join.png" height="333" style="border: 5px solid orange">',
        unsafe_allow_html=True,
    )