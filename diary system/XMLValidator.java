import org.xml.sax.SAXException;
import javax.xml.XMLConstants;
import javax.xml.transform.stream.StreamSource;
import javax.xml.validation.Schema;
import javax.xml.validation.SchemaFactory;
import javax.xml.validation.Validator;
import java.io.File;
import java.io.IOException;

public class XMLValidator {

    public static boolean validateXML(String schemaFile, String xmlFile) throws SAXException, IOException {
        // Create a SchemaFactory capable of understanding WXS schemas
        SchemaFactory factory = SchemaFactory.newInstance(XMLConstants.W3C_XML_SCHEMA_NS_URI);

        // Load a WXS schema, represented by a Schema instance
        Schema schema = factory.newSchema(new File(schemaFile));

        // Create a Validator object, which can be used to validate an instance document
        Validator validator = schema.newValidator();

        // Validate the XML file against the schema
        try {
            validator.validate(new StreamSource(new File(xmlFile)));
            return true;
        } catch (SAXException e) {
            System.out.println("Validation error: " + e.getMessage());
            return false;
        }
    }

    public static void main(String[] args) {
        if (args.length != 2) {
            System.out.println("Usage: XMLValidator <schemaFile> <xmlFile>");
            System.exit(1);
        }

        String schemaFile = args[0];
        String xmlFile = args[1];

        try {
            boolean isValid = validateXML(schemaFile, xmlFile);
            System.out.println("XML is valid: " + isValid);
        } catch (SAXException | IOException e) {
            e.printStackTrace();
        }
    }
}
