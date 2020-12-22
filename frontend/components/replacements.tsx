import React, {
  forwardRef,
} from 'react';

import 'style/replacements.css';

const divInsertClass = (_class : string) => (props) => {
  const {className, children, rest} = props;
  return (
    <div className={`${className ?? ''} ${_class}`} {...rest}>
      {children}
    </div>
  );
};

export const Table = divInsertClass('table');
export const Tr = divInsertClass('tr');
export const Thead = divInsertClass('thead');
export const Tbody = divInsertClass('tbody');
export const Tfoot = divInsertClass('tfoot');
export const Col = divInsertClass('col');
export const Colgroup = divInsertClass('colgroup');
export const Td = divInsertClass('td');
export const Th = divInsertClass('th');
export const Caption = divInsertClass('caption');

export const Link = (props) => {
  const {load, children, ...rest} = props;
  return (
    <a
      onClick={(e) => {
        if (e.altKey || e.ctrlKey || e.shiftKey) return;
        if (load) {
          e.preventDefault();
          load();
        }
      }}
      {...rest}
    >
      {children}
    </a>
  );
};

export const Input = forwardRef<any, any>((props, ref) => {
  const {textarea, ...rest} = props;
  const Element = textarea ? 'textarea' : 'input';
  const onKeyDown = props.onKeyDown || ((e) => {
    switch (e.key) {
      case 'Enter':
        if (!(textarea && e.shiftKey)) e.target.blur();
        break;
      case 'Escape':
        // firefox doesn't blur on escape automatically
        e.target.blur();
        break;
    }
  });

  return (
    <Element
      ref={ref}
      type='text'
      onKeyDown={onKeyDown}
      {...rest}
    />
  );
});

