class App {
  constructor(options = {}) {
    const defaults = {
      project: 'mary-church-terrell',
      q: 'Dearest Mollie',
      searchLimit: 250,
      wordPad: 8,
    };
    const qparams = StringUtil.queryParams();
    this.options = _.extend({}, defaults, options, qparams);
    this.init();
  }

  init() {
    this.initialized = true;

    // UI elements that we will use often
    this.$app = $('#app');
    this.$message = $('#search-results-message');
    this.$query = $('#search-query');
    this.$searchForm = $('#search-form');
    this.$searchSubmit = $('#search-form button[type="submit"]');
    this.$results = $('#search-results-list');
    this.$item = $('#search-results-item');

    // parse templates
    _.templateSettings = {
      interpolate: /\{\{(.+?)\}\}/g,
    };
    this.searchResultItemTemplate = _.template($('#search-result-list-item-template').html());
    this.searchItemTemplate = _.template($('#search-result-item-template').html());

    // load transcirpt data
    const transcriptsPromise = this.loadTranscriptData();
    $.when(transcriptsPromise).done(() => {
      this.onReady();
    }).fail(() => {
      // eslint-disable-next-line no-alert
      alert('Unable to load transcript data');
    });
  }

  static getHighlightedText(text, textToHighlight, wordsBeforeCount, wordsAfterCount) {
    const regex = new RegExp(textToHighlight.split(/\s+/).filter((i) => i?.length).join('|'), 'gi');
    const textNormalized = text.replace(/\s+/g, ' ');
    const result = textNormalized.replace(regex, (match) => `<strong>${match}</strong>`);
    const resultNormalized = result.replaceAll(/<\/strong>\s*<strong>/gi, ' ');
    const indexStart = resultNormalized.indexOf('<strong>');
    const indexEnd = resultNormalized.indexOf('</strong>') + '</strong>'.length;
    const textBefore = resultNormalized.substring(0, indexStart).trim().replaceAll(/<\/?strong>/gi, '');
    const textAfter = resultNormalized.substring(indexEnd).trim().replaceAll(/<\/?strong>/gi, '');
    let wordsBefore = textBefore.split(' ');
    let wordsAfter = textAfter.split(' ');
    if (wordsBefore.length > wordsBeforeCount) {
      wordsBefore = wordsBefore.slice(wordsBefore.length - wordsBeforeCount, wordsBefore.length);
    }
    if (wordsAfter.length > wordsAfterCount) {
      wordsAfter = wordsAfter.slice(0, wordsAfterCount);
    }
    let highlighted = `${wordsBefore.join(' ')} `;
    highlighted += resultNormalized.substring(indexStart, indexEnd);
    highlighted += ` ${wordsAfter.join(' ')}`;
    return highlighted;
  }

  indexTranscriptData(documents) {
    this.loadingOn('Data parsed; indexing transcript data...');
    const index = new FlexSearch.Index();
    // console.log(documents);
    documents.forEach((document) => {
      index.add(document.id, document.Transcription);
    });
    this.searchIndex = index;
    this.transcriptDataPromise.resolve();
  }

  loadingOff() {
    this.$query.prop('disabled', false);
    this.$searchSubmit.prop('disabled', false);
    this.isLoading = false;
    this.$app.removeClass('loading');
  }

  loadingOn(message) {
    this.$query.prop('disabled', true);
    this.$searchSubmit.prop('disabled', true);
    this.isLoading = true;
    this.$app.addClass('loading');
    this.$message.text(message);
  }

  loadListeners() {
    this.$item.on('change', 'input[name="view"]', () => {
      this.constructor.updateContentViewMode();
    });

    this.$searchForm.on('submit', (e) => {
      e.preventDefault();
      if (!this.isLoading) this.search();
    });

    this.$results.on('click', '.select-item', (e) => {
      const $target = $(e.currentTarget);
      const index = parseInt($target.attr('data-id'), 10);
      this.selectItem(index);
    });
  }

  loadTranscriptData() {
    const dataUrl = `../data/${this.options.project}/transcripts.json`;
    this.transcriptDataPromise = $.Deferred();
    this.loadingOn('Loading transcript data... (0%)');
    let prevComplete = 0;
    $.ajax({
      xhr: () => {
        const xhr = new window.XMLHttpRequest();
        xhr.addEventListener('progress', (evt) => {
          if (evt.lengthComputable) {
            const percentComplete = Math.round((evt.loaded / evt.total) * 100);
            if (percentComplete !== prevComplete) {
              this.loadingOn(`Loading transcript data... (${percentComplete}%)`);
              prevComplete = percentComplete;
            }
          }
        }, false);
        return xhr;
      },
      type: 'GET',
      url: dataUrl,
      success: (data) => this.parseTranscriptData(data),
      error: this.transcriptDataPromise.fail(),
    });
    return this.transcriptDataPromise;
  }

  onReady() {
    const q = this.$query.val().trim();
    if (q.length <= 0) {
      this.$query.val(this.options.q);
    }
    this.search();
    this.loadListeners();
  }

  parseTranscriptData(data) {
    this.loadingOn('Transcript data loaded; parsing data...');
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
    this.indexTranscriptData(documents);
  }

  renderResults(results, query) {
    this.$message.html(`There are <strong>${results.length} results</strong> for ${query}" in the transcript data.`);
    let html = '';
    const { wordPad } = this.options;
    results.forEach((result, i) => {
      const document = this.documents[result];
      const text = document.Transcription;
      const matchText = this.constructor.getHighlightedText(text, query, wordPad, wordPad);
      const data = {
        className: i > 0 ? '' : 'selected',
        id: result,
        matchText,
        sequence: i + 1,
        title: document.Item,
      };
      html += this.searchResultItemTemplate(data);
    });
    this.$results.html(html);
  }

  search() {
    const q = this.$query.val().trim();
    this.$results.empty();
    this.$item.removeClass('active');
    this.loadingOn(`Looking for keyword "${q}" in transcripts...`);
    StringUtil.pushURLState({ q });
    this.searchIndex.searchAsync(q, this.options.searchLimit, (results) => {
      this.renderResults(results, q);
      if (results.length > 0) this.selectItem(results[0]);
      this.loadingOff();
    });
  }

  selectItem(index) {
    $('#search-results-list li').removeClass('selected');
    $(`#search-results-list li[data-id="${index}"]`).addClass('selected');
    const document = this.documents[index];
    const html = this.searchItemTemplate(document);
    this.$item.html(html);
    this.$item.addClass('active');
  }

  static updateContentViewMode() {
    const mode = $('input[name="view"]:checked').val();
    $('.search-results-item-content').attr('data-mode', mode);
  }
}

(function initApp() {
  const app = new App({});
}());
