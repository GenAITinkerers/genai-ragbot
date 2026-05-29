# genai-ragbot

For learning genai start with a ragbot



### Upload documents

- Upload pdf documents in data_source folder
- Upload txt documents in data_souce folder


**Running APP**

local run: Start Streamlit:

<pre class="overflow-visible!" data-start="13695" data-end="13730"><div class="contain-inline-size rounded-2xl relative bg-token-sidebar-surface-primary"><div class="sticky top-9"><div class="absolute end-0 bottom-0 flex h-9 items-center pe-2"><div class="bg-token-bg-elevated-secondary text-token-text-secondary flex items-center gap-4 rounded-sm px-2 font-sans text-xs"></div></div></div><div class="overflow-y-auto p-4" dir="ltr"><code class="whitespace-pre! language-bash"><span><span>streamlit run ui/app.py
</span></span></code></div></div></pre>

**Docker run:**

```
docker build -t myapp:v1 .
```

```
docker run -p 8501:8501 -it --name ragbot1 myapp:v1 /bin/bash
```
