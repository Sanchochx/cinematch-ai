import { parseReply } from '../models/formatReply';
import styles from './FormattedText.module.css';

interface FormattedTextProps {
  text: string;
}

export function FormattedText({ text }: FormattedTextProps): React.JSX.Element {
  return (
    <div className={styles.text}>
      {parseReply(text).map((block, index) => {
        if (block.kind === 'paragraph') {
          return (
            <p key={index}>
              {block.lines.map((line, i) => (
                <span key={i}>
                  {i > 0 && <br />}
                  {line}
                </span>
              ))}
            </p>
          );
        }
        const List = block.kind === 'ordered' ? 'ol' : 'ul';
        return (
          <List key={index}>
            {block.items.map((item, i) => (
              <li key={i}>{item}</li>
            ))}
          </List>
        );
      })}
    </div>
  );
}
