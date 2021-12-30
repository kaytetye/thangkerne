# Thangkerne

The bird app content, remade as a website. 


## TODO
- add about page


## Build

1. Flatten media with the `prepare_media.py` script. This will get audio and images out of the media dir and copy into the output dir.
2. Build the HTML pages with `build_html.py` script. It will read the CSV files in the `content` dir and create an index page, and entry pages for each published entry in the data.


## Deploy

Login to Firebase with `kaytetye.code` account

```
firebase deploy --only hosting
```


## Notes

The content in the following folders is handled by `git-lfs`. 

```
git lfs track 'media/**' 'output/audio/**' 'output/images/**'
```
