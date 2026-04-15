import re
import hashlib

class LogParser:
    def __init__(self, threshold=2):
        self.templates = {}  # ID -> template
        self.template_to_id = {} # template -> ID
        self.threshold = threshold
        self.log_counts = {}

    def clean_log(self, log):
        # Remove variable parts: IP, numbers, dates
        log = re.sub(r'\d+\.\d+\.\d+\.\d+', '<IP>', log)
        log = re.sub(r'\d+', '<NUM>', log)
        # Tokenize by common delimiters
        log = re.sub(r' +', ' ', log).strip()
        return log

    def fit(self, logs):
        for log in logs:
            template = self.clean_log(log)
            self.log_counts[template] = self.log_counts.get(template, 0) + 1
        
        # Build vocabulary from templates meeting threshold
        event_id = 1 # Start from 1
        for template, count in self.log_counts.items():
            if count >= self.threshold:
                self.template_to_id[template] = event_id
                self.templates[event_id] = template
                event_id += 1
        
        # Add special tokens
        self.template_to_id['[MASK]'] = 0
        self.template_to_id['[DIST]'] = event_id
        self.template_to_id['[PAD]'] = -1 # Padding
        
        return self

    def transform(self, logs):
        ids = []
        for log in logs:
            template = self.clean_log(log)
            ids.append(self.template_to_id.get(template, 0)) # Default to 0 ([MASK]) or a new ID if preferred
        return ids

    def get_vocab_size(self):
        return len(self.template_to_id)
