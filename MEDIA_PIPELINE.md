# Media Pipeline in ShadowCrawler

ShadowCrawler includes a built‑in media pipeline designed to detect, normalize, and download media files (images, videos, GIFs, and other assets) discovered during a crawl.

This document explains how the media pipeline works, how spiders interact with it, and how users can customize or extend media handling.

---

## 🖼 Overview

The media pipeline is responsible for:

- Detecting media URLs extracted by spiders or extractors  
- Normalizing filenames and extensions  
- Organizing downloaded files into structured directories  
- Handling retries and failures  
- Respecting checkpoints to avoid duplicate downloads  

The pipeline runs automatically — spiders do not need to implement download logic.

---

## 🔍 How Media Is Detected

Media can be yielded by:

### **1. Extractors**
Extractors often return media via:

```python
yield MediaItem(url=img_url, page=response.url)
```

### **2. Spiders**
Spiders may yield media manually:

```python
yield response.as_media(url)
```

### **3. Automatic Extraction**
ShadowCrawler automatically detects:

- `<img>` tags  
- `<video>` sources  
- `<a>` links to media files  
- Common media extensions (`.jpg`, `.png`, `.gif`, `.mp4`, `.webm`, etc.)  

This behavior can be customized per extractor.

---

## 📁 Directory Structure

By default, media is stored under:

```
downloads/
  domain/
    images/
    videos/
    gifs/
    files/
```

ShadowCrawler automatically:

- Creates directories  
- Categorizes media  
- Avoids overwriting existing files  
- Respects checkpoint state  

---

## 🧠 Filename Normalization

The media pipeline ensures filenames are:

- Safe  
- Unique  
- Predictable  

Normalization includes:

- Removing query strings  
- Extracting file extensions  
- Hashing collisions  
- Lowercasing extensions  

Example:

```
https://example.com/photo.jpg?token=123
→ photo.jpg
```

If a conflict occurs:

```
photo.jpg
photo_1.jpg
photo_2.jpg
```

---

## 🔄 Checkpoint Integration

The media pipeline integrates with the checkpoint system:

- Already‑downloaded media is **not downloaded again**  
- Failed downloads are retried  
- Partial downloads are cleaned up  
- State is saved after each batch  

This makes long‑running crawls safe and resumable.

---

## ⚙ Download Process

For each media item:

1. Normalize URL  
2. Determine media type  
3. Choose output directory  
4. Generate safe filename  
5. Download with retries  
6. Save metadata (optional)  
7. Update checkpoint state  

The pipeline uses efficient streaming downloads to avoid memory spikes.

---

## 🧩 Customizing Media Handling

Spiders or extractors can override:

### **Filtering**
```python
def bad_media(self, url):
    return "tracking" in url
```

### **Custom filenames**
```python
def media_filename(self, url):
    return f"custom_{hash(url)}.jpg"
```

### **Custom directories**
```python
media_subdir = "my_custom_folder"
```

### **Disabling automatic extraction**
```python
auto_extract_media = False
```

---

## 🧪 Example: Yielding Media Manually

```python
async def parse(self, response):
    for img in response.css("img::attr(src)").getall():
        yield response.as_media(img)
```

---

## 🚫 What the Media Pipeline Does NOT Do

To avoid confusion:

- It does **not** modify media files  
- It does **not** transcode or compress  
- It does **not** deduplicate across domains  
- It does **not** upload or sync media  
- It does **not** bypass site protections  

ShadowCrawler only downloads what the spider yields or what the extractor detects.

---

## ❤️ Final Notes

The media pipeline is designed to be:

- automatic  
- predictable  
- safe  
- easy to extend  

Whether you're crawling galleries, video sites, or mixed‑content pages, ShadowCrawler handles media cleanly and efficiently so you can focus on building great spiders.
