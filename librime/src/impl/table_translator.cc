// vim: set sts=2 sw=2 et:
// encoding: utf-8
//
// Copyleft 2011 RIME Developers
// License: GPLv3
//
// 2011-07-10 GONG Chen <chen.sst@gmail.com>
//
#include <rime/candidate.h>
#include <rime/config.h>
#include <rime/engine.h>
#include <rime/schema.h>
#include <rime/segmentation.h>
#include <rime/translation.h>
#include <rime/dict/dictionary.h>
#include <rime/impl/table_translator.h>

namespace rime {

class TableTranslation : public Translation {
 public:
  TableTranslation(const DictEntryIterator& iter,
                   int start,
                   int consumed_input_length)
      : iter_(iter),
        start_(start),
        end_(start + consumed_input_length) {
    set_exhausted(iter.exhausted());
  }

  virtual bool Next() {
    if (exhausted())
      return false;
    iter_.Next();
    set_exhausted(iter_.exhausted());
    return true;
  }

  virtual shared_ptr<Candidate> Peek() {
    if (exhausted())
      return shared_ptr<Candidate>();
    const shared_ptr<DictEntry> &e(iter_.Peek());
    shared_ptr<Candidate> cand(new SimpleCandidate(
        "zh",
        start_,
        end_,
        e->text,
        e->comment));
    return cand;
  }

 private:
  DictEntryIterator iter_;
  int start_;
  int end_;
};

TableTranslator::TableTranslator(Engine *engine)
    : Translator(engine) {
  if (!engine) return;
  Dictionary::Component *component = Dictionary::Require("dictionary");
  if (!component) return;
  dict_.reset(component->Create(engine->schema()));
  dict_->Load();
}

TableTranslator::~TableTranslator() {
}

Translation* TableTranslator::Query(const std::string &input,
                                      const Segment &segment) {
  if (!dict_ || !dict_->loaded())
    return NULL;
  if (!segment.HasTag("abc"))
    return NULL;
  EZLOGGERPRINT("input = '%s', [%d, %d)",
                input.c_str(), segment.start, segment.end);

  Translation *translation = NULL;
  DictEntryIterator iter = dict_->LookupWords(input, true);
  if (!iter.exhausted())
    translation = new TableTranslation(iter,
                                       segment.start,
                                       input.length());
  return translation;
}

}  // namespace rime