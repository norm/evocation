.PHONY: css

CSS=static/css/screen.css

css: $(CSS)

clean:
	rm $(CSS)

$(CSS): static/css/%.css: sass/%.scss
	python -mscss -t compact -o $@ $<
