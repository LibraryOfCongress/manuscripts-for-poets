class App {
  constructor(options = {}) {
    const defaults = {
      project: 'mary-church-terrell',
    };
    const qparams = StringUtil.queryParams();
    this.options = _.extend({}, defaults, options, qparams);
    this.init();
  }

  init() {
    this.currentPromptIndex = -1;

    this.$main = $('#main-content');
    this.$intro = $('#intro');
    this.$prompt = $('#prompt-text');
    this.$meta = $('#meta');
    this.$documentModal = $('#document-browser');

    const promptDataURL = `../data/${this.options.project}/prompts.json`;
    const promptDataPromise = $.getJSON(promptDataURL, (data) => data);

    const transcriptDataURL = `../data/${this.options.project}/prompts-docs.json`;
    const transcriptDataPromise = $.getJSON(transcriptDataURL, (data) => data);
    const imagePromise = $.Deferred();

    // wait to load collage images
    const imagePromises = [];
    $('.collage-image').each((index, imgEl) => {
      const promise = new Promise((resolve, reject) => {
        const src = imgEl.getAttribute('src');
        const img = new Image();
        img.src = src;
        if (img.completed) resolve(imgEl);
        else {
          img.onload = () => {
            resolve(imgEl);
          };
        }
      });
      imagePromises.push(promise);
    });
    Promise.all(imagePromises).then((images) => {
      console.log('Loaded all images');
      this.onImageLoad(images);
      imagePromise.resolve(images);
    });

    $.when(promptDataPromise, transcriptDataPromise, imagePromise).done((pdata, tdata, idata) => {
      this.onTranscriptDataLoad(tdata[0].docs);
      this.onPromptDataLoad(pdata[0]);
    });
  }

  loadListeners() {
    $('.start').on('click', (e) => {
      $('.app').addClass('active');
      $('.intro').removeClass('active');
    });

    $('.close-modal').on('click', (e) => {
      $(e.currentTarget).closest('.modal').removeClass('active');
    });

    $('.next-prompt').on('click', (e) => {
      this.renderNextPrompt();
    });

    this.$meta.on('click', '.show-doc', (e) => {
      this.showDocument();
    });
  }

  onImageLoad(images) {
    const $container = $('#collage');
    const containerW = $container.width();
    const containerH = $container.height();
    const imageData = images.map((image, i) => ({ i, image }));
    images.forEach((image, i) => {
      const $image = $(image);
      imageData[i].$image = $image;
      const x = parseFloat($image.attr('data-x'));
      const y = parseFloat($image.attr('data-y'));
      imageData[i].x = x;
      imageData[i].y = y;
      // move images toward the center to start
      const deltaX = (0.5 - x) * containerW;
      let deltaY = containerH;
      if (y < 0.5) deltaY = -containerH;
      $image.css({
        transform: `translate3d(${deltaX}px, ${deltaY}px, 0)`,
      });
      // animate the images back to the original position
      const transitionDuration = MathUtil.lerp(0.5, 2, Math.random());
      const delayN = (0.5 - Math.abs(0.5 - x)) * 2; // delay longer for images in center
      const delayDuration = parseInt(MathUtil.lerp(100, 1000, delayN), 10);
      setTimeout(() => {
        $image.css({
          opacity: 1,
          transition: `opacity ${transitionDuration}s ease-in-out, transform ${transitionDuration}s ease-in-out`,
          transform: 'translate3d(0, 0, 0)',
        });
      }, delayDuration);
    });

    const $window = $(window);
    let windowW = $window.width();
    let windowH = $window.height();
    $window.on('resize', (e) => {
      windowW = $window.width();
      windowH = $window.height();
    });

    setTimeout(() => {
      $container.css('opacity', '0.075');
      this.$intro.addClass('active');
      $('.collage-image').css('transition', 'none');
      // move the images when the mouse moves
      this.$main.on('mousemove', (e) => {
        const { clientX, clientY } = e;
        let nx = MathUtil.clamp(clientX / windowW);
        let ny = MathUtil.clamp(clientY / windowH);
        nx = MathUtil.lerp(1, -1, nx);
        ny = MathUtil.lerp(1, -1, ny);
        imageData.forEach((im) => {
          const { $image, x, y } = im;
          const imx = MathUtil.lerp(-1, 1, x);
          const imy = MathUtil.lerp(-1, 1, y);
          const dx = imx * nx;
          const dy = imy * ny;
          const deltaX = dx * 50;
          const deltaY = dy * 50;
          $image.css('transform', `translate3d(${deltaX}px, ${deltaY}px, 0)`);
        });
      });
    }, 3000);
  }

  onPromptDataLoad(data) {
    console.log('Prompt data loaded.');

    this.prompts = DataUtil.loadCollectionFromRows(data.prompts, (prompt) => {
      const updatedPrompt = prompt;
      updatedPrompt.Project = prompt.Project.replace(/:.+/i, '');
      updatedPrompt.itemUrl = `https://www.loc.gov/resource/${prompt.ResourceID}/?sp=${prompt.ItemAssetIndex}&st=text`;
      return updatedPrompt;
    }, true);
    this.prompts = _.shuffle(this.prompts);
    this.promptCount = this.prompts.length;
    this.timeRange = data.timeRange;
    this.subCollections = data.subCollections;

    this.promptDataLoaded = true;
    this.$main.removeClass('is-loading');
    this.renderNextPrompt();
    this.loadListeners();
  }

  onTranscriptDataLoad(transcriptData) {
    this.documents = DataUtil.loadCollectionFromRows(transcriptData, (doc) => {
      const updatedDoc = doc;
      updatedDoc.id = doc.index;
      updatedDoc.itemUrl = `https://www.loc.gov/resource/${doc.ResourceID}/?sp=${doc.ItemAssetIndex}&st=text`;
      updatedDoc.DownloadUrl = `https://tile.loc.gov/image-services/iiif/${doc.DownloadUrl}/full/pct:100/0/default.jpg`;
      return updatedDoc;
    }, true);
    console.log('Transcript data loaded.');
    this.transcriptsLoaded = true;
  }

  renderDocument() {
    const {
      documents, $documentModal, currentPromptIndex, prompts,
    } = this;
    const prompt = prompts[currentPromptIndex];
    const doc = documents[prompt.doc];
    const $document = $documentModal.find('#document-container');
    const $title = $documentModal.find('.resource-link');
    const text = doc.Transcription.replace(/\s+/g, ' ').replace(/\s\s+/g, ' ');
    const matchText = text.replace(prompt.text, `<strong>${prompt.text}</strong>`);
    let html = '';
    html += `<div class="pane transcript"><p>${matchText}</p></div>`;
    html += `<div class="pane image" style="background-image: url(${doc.DownloadUrl})"></div>`;
    $document.html(html);
    $title.text(doc.Item);
    $title.attr('href', doc.itemUrl);
  }

  renderNextPrompt() {
    this.currentPromptIndex += 1;
    if (this.currentPromptIndex >= this.promptCount) this.currentPromptIndex = 0;
    const prompt = this.prompts[this.currentPromptIndex];
    this.$prompt.html(`<p>${prompt.text}</p>`);

    let html = '';
    html += '<h2>Mary Church Terrell Papers</h2>';
    html += `<h3>${prompt.Item} <button class="show-doc">View in context</button></h3>`;
    this.$meta.html(html);
    // const variance = 5;
    // const r = Math.round(MathUtil.lerp(102 - variance, 102 + variance, Math.random()));
    // const g = Math.round(MathUtil.lerp(71 - variance, 71 + variance, Math.random()));
    // const b = Math.round(MathUtil.lerp(32 - variance, 32 + variance, Math.random()));
    // const alpha = MathUtil.lerp(0.25, 1, Math.random());
    // this.$main.css('background-color', `rgba(${r}, ${g}, ${b}, ${alpha})`);
    this.renderDocument();
  }

  showDocument() {
    this.$documentModal.addClass('active');
  }
}

(function initApp() {
  const app = new App({});
}());
