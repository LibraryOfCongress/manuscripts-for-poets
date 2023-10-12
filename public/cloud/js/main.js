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
    this.$main = $('.main-content').first();

    const timelineDataURL = `../data/${this.options.project}/cloud.json`;
    const timelineDataPromise = $.getJSON(timelineDataURL, (data) => data);

    const transcriptDataURL = `../data/${this.options.project}/transcripts.json`;
    const transcriptDataPromise = $.getJSON(transcriptDataURL, (data) => data);
    this.transcriptDataPromise = $.Deferred();

    $.when(timelineDataPromise).done((data) => {
      this.onCloudDataLoad(data);
    });

    $.when(transcriptDataPromise).done((data) => {
      this.onTranscriptDataLoad(data);
      this.transcriptDataPromise.resolve();
    });
  }

  loadListeners() {
    $('.start').on('click', (e) => {
      $('.app').addClass('active');
      $('.intro').removeClass('active');
    });

    this.$main.on('change', '.facet', (e) => {

    });
  }

  onCloudDataLoad(data) {
    console.log('Coud data loaded.');

    this.words = DataUtil.loadCollectionFromRows(data.words, false, true);
    this.wordBuckets = DataUtil.loadCollectionFromRows(data.wordBuckets, false, true);
    this.wordDocs = _.chunk(data.wordDocs, 2);

    this.facets = [];
    this.facets.push({
      id: 'subCollections',
      label: 'Sub-collection',
      type: 'select',
      values: data.subCollections,
    });
    this.facets.push({
      id: 'partsOfSpeech',
      label: 'Part of speech',
      type: 'select',
      values: data.partsOfSpeech,
    });
    this.facets.push({
      id: 'sentiment',
      label: 'Sentiment (negative to positive)',
      type: 'range',
      minValue: 0,
      maxValue: 1,
      step: 0.01,
    });
    this.cloudDataLoaded = true;

    this.$main.removeClass('is-loading');
    this.loadListeners();
  }

  onTranscriptDataLoad(transcriptData) {
    this.documents = DataUtil.loadCollectionFromRows(transcriptData, (doc) => {
      const updatedDoc = doc;
      updatedDoc.id = doc.index;
      updatedDoc.itemUrl = `https://www.loc.gov/resource/${doc.ResourceID}/?sp=${doc.ItemAssetIndex}&st=text`;
      return updatedDoc;
    });
    console.log('Transcript data loaded.');
    this.transcriptsLoaded = true;
  }
}

(function initApp() {
  const app = new App({});
}());
