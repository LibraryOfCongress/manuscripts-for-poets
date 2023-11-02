class StringUtil {
  static getHighlightedText(text, textToHighlight, wordsBeforeCount = -1, wordsAfterCount = -1) {
    const regex = new RegExp(textToHighlight.split(/\s+/).filter((i) => i?.length).join('|'), 'gi');
    const textNormalized = text.replace(/\s+/g, ' ');
    const result = textNormalized.replace(regex, (match) => `<strong>${match}</strong>`);
    const resultNormalized = result.replaceAll(/<\/strong>\s*<strong>/gi, ' ');
    let highlighted = resultNormalized;
    if (wordsBeforeCount > 0 || wordsAfterCount > 0) {
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
      highlighted = `${wordsBefore.join(' ')} `;
      highlighted += resultNormalized.substring(indexStart, indexEnd);
      highlighted += ` ${wordsAfter.join(' ')}`;
    }
    return highlighted;
  }

  static loadFromStorage(key) {
    const value = window.localStorage.getItem(key);
    return value ? JSON.parse(value) : false;
  }

  static loadTemplateFromElement(id, renderer, data) {
    const templateString = document.getElementById(id.replace('#', '')).innerHTML;
    return StringUtil.loadTemplateFromString(templateString, renderer, data);
  }

  static loadTemplateFromString(templateString, renderer, data) {
    let rendered = renderer.render(templateString, data);
    rendered = rendered.replace(/>\s+</g, '><');
    return rendered;
  }

  static pushURLState(data, replace = false) {
    if (window.history.pushState) {
      const baseUrl = window.location.href.split('?')[0];
      const currentState = window.history.state;
      const urlEncoded = $.param(data);
      const newUrl = `${baseUrl}?${urlEncoded}`;

      // ignore if state is the same
      if (currentState) {
        const currentEncoded = $.param(currentState);
        const currentUrl = `${baseUrl}?${currentEncoded}`;
        if (newUrl === currentUrl) return;
      }

      window.historyInitiated = true;
      if (replace === true) window.history.replaceState(data, '', newUrl);
      else window.history.pushState(data, '', newUrl);
    }
  }

  static queryParams() {
    const searchString = window.location.search;
    if (searchString.length <= 0) return {};
    const search = searchString.substring(1);
    const jsonFormatted = search.replace(/&/g, '","').replace(/=/g, '":"');
    const parsed = JSON.parse(`{"${jsonFormatted}"}`, (key, value) => (key === '' ? value : decodeURIComponent(value)));
    _.each(parsed, (value, key) => {
      const dkey = decodeURIComponent(key);
      parsed[dkey] = value;
    });
    return parsed;
  }

  static saveToStorage(key, value) {
    window.localStorage.setItem(key, JSON.stringify(value));
  }
}
