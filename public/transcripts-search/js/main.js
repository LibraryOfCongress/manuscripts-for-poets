class App {
  constructor(options = {}) {
    const defaults = {
      project: 'mary-church-terrell-correspondence',
    };
    this.options = _.extend({}, defaults, options);
    this.init();
  }

  init() {
    this.initialized = true;
    const transcriptsPromise = this.loadTranscriptData();
    $.when(transcriptsPromise).done(() => {
      this.onReady();
    }).fail(() => {
      // eslint-disable-next-line no-alert
      alert('Unable to load transcript data');
    });
  }

  loadListeners() {
    $('input[name="view"]').on('change', () => {
      this.constructor.updateContentViewMode();
    });
  }

  loadTranscriptData() {
    const dataUrl = `../data/${this.options.project}/transcripts.json"`;
    this.transcriptDataPromise = $.Deferred();
    console.log('Downloading JSON data...');
    $.getJSON(dataUrl, (data) => this.onLoadTranscriptData(data))
      .fail(() => this.transcriptDataPromise.fail());
    return this.transcriptDataPromise;
  }

  onLoadTranscriptData(data) {
    const { rows, cols, groups } = data;
    this.transcriptDataPromise.resolve();
  }

  onReady() {
    this.loadListeners();
  }

  static updateContentViewMode() {
    const mode = $('input[name="view"]:checked').val();
    $('.search-results-item-content').attr('data-mode', mode);
  }
}

(function initApp() {
  const app = new App({});
}());
