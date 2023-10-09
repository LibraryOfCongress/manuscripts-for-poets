class App {
  constructor(options = {}) {
    const defaults = {
      project: 'mary-church-terrell',
      subCollection0: 2,
      subCollection1: 4,
    };
    const qparams = StringUtil.queryParams();
    this.options = _.extend({}, defaults, options, qparams);
    this.init();
  }

  init() {
    this.$subCollectionSelects = $('.select-sub-collection');

    const timelineDataURL = `../data/${this.options.project}/timeline.json`;
    const timelineWordsURL = `../data/${this.options.project}/timeline-words.json`;
    const timelineTranscriptsURL = `../data/${this.options.project}/timeline-transcripts.json`;
    const timelineDataPromise = $.getJSON(timelineDataURL, (data) => data);
    const timelineWordsPromise = $.getJSON(timelineWordsURL, (data) => data);
    const timelineTranscriptPromise = $.getJSON(timelineTranscriptsURL, (data) => data);

    $.when(timelineDataPromise, timelineWordsPromise).done((timelineData, wordsData) => {
      this.onTimelineDataLoad(timelineData[0], wordsData[0]);
    });

    $.when(timelineTranscriptPromise).done((transcriptData) => {
      this.onTranscriptDataLoad(transcriptData);
    });
  }

  loadListeners() {
    this.$subCollectionSelects.on('change', (e) => {
      this.onChangeSubCollection();
    });
  }

  onChangeSubCollection() {
    const { $subCollectionSelects } = this;
  }

  onTimelineDataLoad(timelineData, wordsData) {
    console.log('Timeline data loaded.');

    const { rows, cols, groups } = wordsData;
    const words = _.map(rows, (row, i) => {
      const word = _.object(cols, row);
      // parse grouped values
      _.each(groups, (values, field) => {
        word[field] = values[word[field]];
      });
      // add additional values
      word.id = i;
      return word;
    });
    this.words = words;
    this.timelineData = timelineData;

    this.renderSubCollections();
    this.renderYears();
    this.loadListeners();
    this.renderTimelne();
  }

  onTranscriptDataLoad(data) {
    console.log('Transcript data loaded.');
    const { rows, cols, groups } = data;
    const documents = _.map(rows, (row, i) => {
      const doc = _.object(cols, row);
      // parse grouped values
      _.each(groups, (values, field) => {
        doc[field] = values[doc[field]];
      });
      // add additional values
      doc.id = i;
      doc.itemUrl = `https://www.loc.gov/resource/${doc.ResourceID}/?sp=${doc.ItemAssetIndex}&st=text`;
      return doc;
    });
    this.documents = documents;
  }

  renderSubCollections() {
    const { timelineData, $subCollectionSelects } = this;
    $subCollectionSelects.each((i, el) => {
      const $el = $(el);
      let html = '';
      const defaultValue = this.options[`subCollection${i}`];
      timelineData.forEach((container, j) => {
        const selected = defaultValue === j ? ' selected' : '';
        html += `<option value="${j}"${selected}>${container.title}</option>`;
      });
      $el.html(html);
    });
  }

  renderSubCollectionTimeline($timeline, years) {
    const { words } = this;
    let html = '';
    years.forEach((yearData) => {
      const { year, lemmas } = yearData;
      html += `<div class="year" data-year="${year}">`;
      lemmas.forEach((wordData) => {
        const [wordIndex, count] = wordData;
        const word = words[wordIndex];
        html += `<button class="word">${word.lemma}</button>`;
      });
      html += '</div>';
    });
    $timeline.html(html);
  }

  renderTimelne() {
    const { timelineData, $subCollectionSelects } = this;

    $subCollectionSelects.each((i, el) => {
      const $el = $(el);
      const prevValue = parseInt($el.attr('data-value'), 10);
      const currentValue = parseInt($el.val(), 10);
      if (prevValue === currentValue) return;
      $el.attr('data-value', currentValue);
      const $timeline = $($el.attr('data-target'));
      this.renderSubCollectionTimeline($timeline, timelineData[currentValue].years);
    });
  }

  renderYears() {
    const { timelineData } = this;
    const yearCount = timelineData[0].years.length;
    const wrapperWidth = yearCount * 400;
    console.log(wrapperWidth);
    $('.timeline-wrapper').css('width', `${wrapperWidth}px`);
  }
}

(function initApp() {
  const app = new App({});
}());
