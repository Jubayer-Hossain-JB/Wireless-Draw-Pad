self.oninstall = (e)=>{
    e.waitUntil(caches.open('web-img').then((cache)=>{
        cache.addAll([
            '/trash.png',
            '/brush.png',
            '/back.png',
        ])
    }))
}

self.addEventListener('fetch', event=>{
    if(caches.match(event.request)){
        event.respondWith(caches.match(event.request))
    }
  })
  
  
  