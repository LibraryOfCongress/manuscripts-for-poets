class App {
  constructor(options = {}) {
    const defaults = {
      project: 'mary-church-terrell',
    };
    this.options = _.extend({}, defaults, options);
    this.init();
  }

  init() {
    this.defaultState = {
      filters: {
        Project: 'any',
        EstimatedYear: 'any',
      },
      prompt: -1,
    };
    const qparams = StringUtil.queryParams();
    this.setState(qparams);

    this.$main = $('#main-content');
    this.$intro = $('#intro');
    this.$prompt = $('#prompt-text');
    this.$meta = $('#meta');
    this.$documentModal = $('#document-browser');
    this.$statePrev = $('.state-prev');
    this.$stateNext = $('.state-next');

    this.stateHistory = [];
    this.stateIndex = -1;

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

    this.loadFilters();
    this.renderFilters();
    $.when(promptDataPromise, transcriptDataPromise, imagePromise).done((pdata, tdata, idata) => {
      this.onTranscriptDataLoad(tdata[0].docs);
      this.onPromptDataLoad(pdata[0]);
    });
  }

  filterPrompts(resetIndex = true) {
    const { prompts, state } = this;

    const filteredPrompts = prompts.filter((prompt) => {
      let isVisible = true;
      _.each(state.filters, (currentValue, key) => {
        const pvalue = prompt[key];
        if (currentValue !== 'any') {
          if (key === 'EstimatedYear' && currentValue.includes('-')) {
            const [start, end] = currentValue.split('-', 2).map((v) => parseInt(v, 10));
            if (pvalue !== '' && (pvalue < start || pvalue >= end)) isVisible = false;
          } else if (pvalue !== currentValue) isVisible = false;
        }
      });
      return isVisible;
    });

    // hack: if not enough prompts, remove the year filter
    if (filteredPrompts.length <= 3) {
      console.log('Not enough prompts for this filter combination. Removing date filter.');
      const $button = $('#time-period-any');
      this.onFilter($button);
      return;
    }

    // randomize prompts
    this.filteredPrompts = _.shuffle(filteredPrompts);

    // prioritize starred prompts
    const prioritizeStarred = 3;
    let starred = this.filteredPrompts.filter((p) => p.tag === 'starred');
    if (starred.length > prioritizeStarred) starred = starred.slice(0, prioritizeStarred);
    if (starred.length > 0) {
      const starredTexts = _.pluck(starred, 'text');
      const unstarred = this.filteredPrompts.filter((p) => starredTexts.indexOf(p.text) < 0);
      this.filteredPrompts = starred.concat(unstarred);
    }

    if (resetIndex) this.state.prompt = -1;
  }

  static getPrompt(prompts, index) {
    let prompt = _.findWhere(prompts, { index });
    if (prompt === undefined) prompt = _.first(prompts);
    return prompt;
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

    $('.dropdown-selected').on('click', (e) => {
      this.constructor.toggleMenu($(e.currentTarget));
    });

    $('.dropdown-list-item').on('click', (e) => {
      this.onFilter($(e.currentTarget));
    });

    this.$meta.on('click', '.show-doc', (e) => {
      this.showDocument();
    });

    this.$statePrev.on('click', (e) => {
      window.history.back();
    });

    this.$stateNext.on('click', (e) => {
      window.history.forward();
    });

    window.addEventListener('popstate', (event) => {
      this.onPopState(event.state);
    });
  }

  loadFilters() {
    const dataFilters = {};
    $('.data-option').each((i, el) => {
      const name = el.getAttribute('data-name');
      const value = el.getAttribute('data-value');
      if (_.has(dataFilters, name)) {
        dataFilters[name].values.push(value);
      } else {
        dataFilters[name] = { values: [value] };
      }
    });
    this.dataFilters = dataFilters;
  }

  onFilter($selectButton) {
    this.constructor.renderFilterSelect($selectButton);
    const name = $selectButton.attr('data-name');
    const value = $selectButton.attr('data-value');
    this.state.filters[name] = value;
    this.filterPrompts();
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
        transform: `translate(${deltaX}px, ${deltaY}px)`,
      });
      // animate the images back to the original position
      const transitionDuration = MathUtil.lerp(0.5, 2, Math.random());
      const delayN = (0.5 - Math.abs(0.5 - x)) * 2; // delay longer for images in center
      const delayDuration = parseInt(MathUtil.lerp(100, 1000, delayN), 10);
      setTimeout(() => {
        $image.css({
          opacity: 1,
          transition: `opacity ${transitionDuration}s ease-in-out, transform ${transitionDuration}s ease-in-out`,
          transform: 'translate(0, 0)',
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
      $container.css('opacity', '0.333');
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
          $image.css('transform', `translate(${deltaX}px, ${deltaY}px)`);
        });
      });
    }, 3000);
  }

  onPopState(state) {
    this.setState(state);
    this.filterPrompts(false);
    this.renderFilters();
    this.renderPrompt();

    // activate or deactivate prev/next buttons based on where we are in state history
    const stateString = $.param(state);
    let stateIndex = _.indexOf(this.stateHistory, stateString);
    // state not found; probably from previous history
    if (stateIndex < 0) {
      // add it to the beginning of the history
      this.stateHistory.unshift(stateString);
      stateIndex = 0;
    }
    this.stateIndex = stateIndex;
    this.renderStateButtons();
  }

  onPromptDataLoad(data) {
    console.log('Prompt data loaded.');

    this.prompts = DataUtil.loadCollectionFromRows(data.prompts, (prompt) => {
      const updatedPrompt = prompt;
      // updatedPrompt.Project = prompt.Project.replace(/:.+/i, '');
      updatedPrompt.itemUrl = `https://www.loc.gov/resource/${prompt.ResourceID}/?sp=${prompt.ItemAssetIndex}&st=text`;
      return updatedPrompt;
    }, true);
    this.filterPrompts(false);
    this.timeRange = data.timeRange;
    this.subCollections = data.subCollections;

    // this.printBuckets();

    this.promptDataLoaded = true;
    this.$main.removeClass('is-loading');
    if (this.state.prompt >= 0) {
      this.renderPrompt();
      this.pushState();
    } else this.renderNextPrompt();
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

  static preloadImage(url) {
    const img = new Image();
    img.src = url;
  }

  printBuckets() {
    const { dataFilters, prompts } = this;
    const buckets = [];
    const promptFilter = (prompt, key, value) => {
      if (Array.isArray(value)) {
        return prompt[key] === '' || (prompt[key] >= value[0] && prompt[key] < value[1]);
      }
      return prompt[key] === value;
    };
    let level = 0;
    _.each(dataFilters, (dataFilter, key) => {
      const entries = dataFilter.values;
      level += 1;
      entries.forEach((value) => {
        const bucketKey = (typeof value === 'string') ? value : value.toString();
        if (level === 1) {
          const matches = _.filter(prompts, (prompt) => promptFilter(prompt, key, value));
          buckets.push({ bname: bucketKey, bprompts: matches, blevel: level });
        } else {
          buckets.forEach(({ bname, bprompts, blevel }) => {
            if (blevel === (level - 1)) {
              const newKey = `${bname}-${bucketKey}`;
              const newPrompts = _.filter(bprompts, (prompt) => promptFilter(prompt, key, value));
              buckets.push({ bname: newKey, bprompts: newPrompts, blevel: level });
            }
          });
        }
      });
    });

    const printBuckets = buckets.filter((bucket) => bucket.blevel === level);
    console.log(printBuckets);
  }

  pushState() {
    const { state, defaultState } = this;
    const urlState = {};
    _.each(state.filters, (value, key) => {
      if (defaultState.filters[key] !== value) {
        urlState[key] = value;
      }
      if (state.prompt !== defaultState.prompt) urlState.prompt = state.prompt;
    });
    // console.log(state, defaultState, urlState);
    StringUtil.pushURLState(urlState);

    // keep track of state
    const newStateHistory = this.stateIndex >= 0
      ? this.stateHistory.slice(0, this.stateIndex + 1)
      : this.stateHistory.slice();
    newStateHistory.push($.param(urlState));
    this.stateHistory = newStateHistory;
    this.stateIndex = this.stateHistory.length - 1;
    this.renderStateButtons();
  }

  renderDocument() {
    const {
      documents, $documentModal, state, filteredPrompts,
    } = this;
    const prompt = this.constructor.getPrompt(filteredPrompts, state.prompt);
    const doc = documents[prompt.doc];
    const $document = $documentModal.find('#document-container');
    const $title = $documentModal.find('.resource-link');
    const text = doc.Transcription.replace(/\s+/g, ' ').replace(/\s\s+/g, ' ');
    const matchText = text.replace(prompt.text, `</span><strong>${prompt.text}</strong><span>`);
    let html = '';
    html += `<div id="transcript-pane" class="pane transcript"><p><span>${matchText}</span></p></div>`;
    html += `<div class="pane image" style="background-image: url(${doc.DownloadUrl})"></div>`;
    $document.html(html);
    $title.text(doc.Item);
    $title.attr('href', doc.itemUrl);
    // this.constructor.preloadImage(doc.DownloadUrl);
    // check if highligthed text is visible
    setTimeout(() => {
      const $pane = $('#transcript-pane');
      const $highlighted = $pane.find('strong').first();
      if ($highlighted.length > 0) {
        const $transcript = $pane.find('p').first();
        const pHeight = $pane.height();
        const highlightedY = $highlighted.position().top;
        const thresholdTop = pHeight * 0.667;
        const targetTop = pHeight * 0.4;
        if (highlightedY > thresholdTop) {
          // console.log(highlightedY, thresholdTop);
          const tHeight = $transcript.height();
          const maxTop = tHeight - pHeight;
          const pScrollTop = Math.min(highlightedY - targetTop, maxTop);
          if (pScrollTop > 0) {
            $pane.scrollTop(pScrollTop);
          }
        }
      }
    }, 100);
  }

  renderFilters() {
    _.each(this.state.filters, (value, key) => {
      const $button = $(`.data-option[data-name="${key}"][data-value="${value}"]`).first();
      this.constructor.renderFilterSelect($button);
    });
  }

  static renderFilterSelect($selectButton) {
    const $dropdown = $selectButton.closest('.dropdown');
    const $selected = $dropdown.find('.dropdown-selected');
    $dropdown.find('.dropdown-list-item').attr('aria-selected', 'false');
    $selectButton.attr('aria-selected', 'true');
    $selected.text($selectButton.find('.option-title').text());
    $selected.attr('aria-expanded', 'false');
    $dropdown.find('.dropdown-list')[0].hidden = true;
  }

  renderNextPrompt() {
    const index = _.findIndex(this.filteredPrompts, (p) => p.index === this.state.prompt);
    let newIndex = index + 1;
    if (newIndex >= this.filteredPrompts.length) newIndex = 0;
    this.state.prompt = this.filteredPrompts[newIndex].index;
    this.renderPrompt();
    this.pushState();
  }

  renderPrompt() {
    const { state, filteredPrompts } = this;
    const prompt = this.constructor.getPrompt(filteredPrompts, state.prompt);
    this.$prompt.html(`<p>${prompt.text}</p>`);

    let html = '';
    html += '<h2>Mary Church Terrell Papers</h2>';
    html += `<h3>${prompt.Item} <button class="show-doc">View in context</button></h3>`;
    this.$meta.html(html);

    this.renderDocument();
  }

  renderStateButtons() {
    const { stateIndex, stateHistory } = this;
    if (stateIndex >= (stateHistory.length - 1)) this.$stateNext.removeClass('active');
    else this.$stateNext.addClass('active');
    if (stateIndex <= 0) this.$statePrev.removeClass('active');
    else this.$statePrev.addClass('active');
  }

  setState(data) {
    const state = structuredClone(this.defaultState);
    _.each(state.filters, (value, name) => {
      if (_.has(data, name)) {
        state.filters[name] = data[name];
      }
    });
    if (_.has(data, 'prompt')) state.prompt = parseInt(data.prompt, 10);
    this.state = state;
  }

  showDocument() {
    this.$documentModal.addClass('active');
  }

  static toggleMenu($menuButton) {
    const value = $menuButton.attr('aria-expanded');
    const controls = $menuButton.attr('aria-controls');
    const sublist = $(`#${controls}`)[0];
    if (value === 'true') {
      $menuButton.attr('aria-expanded', 'false');
      sublist.hidden = true;
    } else {
      $menuButton.attr('aria-expanded', 'true');
      sublist.hidden = false;
    }
  }
}

(function initApp() {
  const app = new App({});
}());