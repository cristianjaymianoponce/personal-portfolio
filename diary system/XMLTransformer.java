import java.io.File;
import java.io.IOException;
import javax.xml.transform.Transformer;
import javax.xml.transform.TransformerException;
import javax.xml.transform.TransformerFactory;
import javax.xml.transform.stream.StreamResult;
import javax.xml.transform.stream.StreamSource;

public class XMLTransformer {

    public static void main(String[] args) {
        if (args.length != 3) {
            System.out.println("Usage: XMLTransformer <xml file> <xslt file> <output file>");
            return;
        }

        String xmlFile = args[0];
        String xsltFile = args[1];
        String outputFile = args[2];

        try {
            transformXML(xmlFile, xsltFile, outputFile);
            System.out.println("Transformation successful");
        } catch (TransformerException | IOException e) {
            System.out.println("Transformation failed");
            e.printStackTrace();
        }
    }

    public static void transformXML(String xmlFile, String xsltFile, String outputFile) throws TransformerException, IOException {
        TransformerFactory factory = TransformerFactory.newInstance();
        Transformer transformer = factory.newTransformer(new StreamSource(new File(xsltFile)));
        transformer.transform(new StreamSource(new File(xmlFile)), new StreamResult(new File(outputFile)));
    }
}
