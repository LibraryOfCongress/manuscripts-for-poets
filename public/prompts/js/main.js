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
    this.$prompt = $('#prompt-text');
    this.$meta = $('#meta');
    this.$documentModal = $('#document-browser');

    const promptDataURL = `../data/${this.options.project}/prompts.json`;
    const promptDataPromise = $.getJSON(promptDataURL, (data) => data);

    const transcriptDataURL = `../data/${this.options.project}/prompts-docs.json`;
    const transcriptDataPromise = $.getJSON(transcriptDataURL, (data) => data);
    this.transcriptDataPromise = $.Deferred();

    $.when(promptDataPromise).done((data) => {
      this.onPromptDataLoad(data);
    });

    $.when(transcriptDataPromise).done((data) => {
      this.onTranscriptDataLoad(data.docs);
      this.transcriptDataPromise.resolve();
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
      this.renderDocument();
    });
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
    $documentModal.addClass('active');
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
    const variance = 5;
    const r = Math.round(MathUtil.lerp(102 - variance, 102 + variance, Math.random()));
    const g = Math.round(MathUtil.lerp(71 - variance, 71 + variance, Math.random()));
    const b = Math.round(MathUtil.lerp(32 - variance, 32 + variance, Math.random()));
    const alpha = MathUtil.lerp(0.25, 1, Math.random());
    this.$main.css('background-color', `rgba(${r}, ${g}, ${b}, ${alpha})`);
  }
}

(function initApp() {
  const app = new App({});
}());
